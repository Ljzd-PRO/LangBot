"""
Chat Logger Plugin for LangBot

This plugin provides comprehensive chat logging functionality, recording group chat messages
and bot responses to a database with configurable filtering options.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pkg.plugin.context import BasePlugin, EventContext
from pkg.plugin.events import GroupMessageReceived, NormalMessageResponded
from pkg.plugin import context


class Base(DeclarativeBase):
    """SQLAlchemy declarative base"""

    pass


class ChatRecord(Base):
    """Chat record model for database storage"""

    __tablename__ = 'chat_records'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    message: Mapped[str] = mapped_column(sa.Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
    group_id: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    is_bot_message: Mapped[bool] = mapped_column(sa.Boolean, default=False)


@context.register(
    name='chat-logger',
    description='A comprehensive chat logging plugin that records group chat messages and bot replies to database',
    version='1.0.0',
    author='LangBot',
)
class ChatLoggerPlugin(BasePlugin):
    """Chat Logger Plugin Implementation"""

    def __init__(self, host):
        super().__init__(host)
        self.logger = logging.getLogger(f'{__name__}.ChatLoggerPlugin')
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self.database_url: str = 'sqlite+aiosqlite:///./chat_logs.db'
        self.database_name: str = 'langbot_chat'
        self.include_bot_messages: bool = True
        self.group_whitelist: list[str] = []
        self.group_blacklist: list[str] = []

    async def initialize(self):
        """Initialize the plugin and database connection"""
        try:
            # Load configuration
            config = self.config or {}
            self.database_url = config.get('database_url', self.database_url)
            self.database_name = config.get('database_name', self.database_name)
            self.include_bot_messages = config.get('include_bot_messages', self.include_bot_messages)
            self.group_whitelist = config.get('group_whitelist', self.group_whitelist)
            self.group_blacklist = config.get('group_blacklist', self.group_blacklist)

            # Initialize database
            await self._init_database()

            self.logger.info(f'Chat Logger Plugin initialized with database: {self.database_name}')
            self.logger.info(f'Group whitelist: {self.group_whitelist}')
            self.logger.info(f'Group blacklist: {self.group_blacklist}')
            self.logger.info(f'Include bot messages: {self.include_bot_messages}')

        except Exception as e:
            self.logger.error(f'Failed to initialize Chat Logger Plugin: {e}')
            raise

    async def _init_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                future=True,
            )

            # Create session factory
            self.session_factory = async_sessionmaker(bind=self.engine, expire_on_commit=False)

            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            self.logger.info('Database tables created successfully')

        except Exception as e:
            self.logger.error(f'Database initialization failed: {e}')
            raise

    def _should_log_group(self, group_id: str) -> bool:
        """Check if messages from this group should be logged"""
        group_id_str = str(group_id)

        # If whitelist is specified and group is not in it, don't log
        if self.group_whitelist and group_id_str not in self.group_whitelist:
            return False

        # If group is in blacklist, don't log
        if group_id_str in self.group_blacklist:
            return False

        return True

    async def _save_chat_record(
        self, user_id: str, nickname: Optional[str], message: str, group_id: str, is_bot_message: bool = False
    ):
        """Save a chat record to the database"""
        if not self.session_factory:
            self.logger.warning('Database not initialized, skipping record save')
            return

        try:
            async with self.session_factory() as session:
                record = ChatRecord(
                    user_id=str(user_id),
                    nickname=nickname,
                    message=message,
                    group_id=str(group_id),
                    is_bot_message=is_bot_message,
                    timestamp=datetime.utcnow(),
                )

                session.add(record)
                await session.commit()

                self.logger.debug(f'Saved chat record from user {user_id} in group {group_id}')

        except Exception as e:
            self.logger.error(f'Failed to save chat record: {e}')

    @context.handler(GroupMessageReceived)
    async def on_group_message_received(self, ctx: EventContext):
        """Handle group message received events"""
        try:
            event: GroupMessageReceived = ctx.event

            # Check if we should log this group
            if not self._should_log_group(event.launcher_id):
                return

            # Extract message text
            message_text = ''
            if hasattr(event.message_chain, 'messages'):
                # Handle MessageChain with messages list
                for msg in event.message_chain.messages:
                    if hasattr(msg, 'text'):
                        message_text += msg.text
                    elif hasattr(msg, 'content') and isinstance(msg.content, str):
                        message_text += msg.content
                    elif isinstance(msg, str):
                        message_text += msg
            elif hasattr(event.message_chain, 'text'):
                # Handle direct text attribute
                message_text = event.message_chain.text
            elif isinstance(event.message_chain, str):
                # Handle direct string
                message_text = event.message_chain
            else:
                # Fallback: convert to string
                message_text = str(event.message_chain)

            # Skip empty messages
            if not message_text.strip():
                return

            # Get nickname if available
            nickname = None
            if hasattr(event, 'sender_name'):
                nickname = event.sender_name
            elif hasattr(ctx.event.query, 'message_event') and hasattr(ctx.event.query.message_event, 'sender'):
                sender = ctx.event.query.message_event.sender
                if hasattr(sender, 'nickname'):
                    nickname = sender.nickname
                elif hasattr(sender, 'card'):
                    nickname = sender.card

            # Save the record
            await self._save_chat_record(
                user_id=event.sender_id,
                nickname=nickname,
                message=message_text,
                group_id=event.launcher_id,
                is_bot_message=False,
            )

        except Exception as e:
            self.logger.error(f'Error handling group message: {e}')

    @context.handler(NormalMessageResponded)
    async def on_normal_message_responded(self, ctx: EventContext):
        """Handle bot response events"""
        try:
            # Skip if bot messages are not included
            if not self.include_bot_messages:
                return

            event: NormalMessageResponded = ctx.event

            # Only log group responses
            if event.launcher_type != 'group':
                return

            # Check if we should log this group
            if not self._should_log_group(event.launcher_id):
                return

            # Combine prefix and response text
            full_response = ''
            if event.prefix:
                full_response += event.prefix
            if event.response_text:
                full_response += event.response_text

            # Skip empty responses
            if not full_response.strip():
                return

            # Get bot user ID from adapter or use a default
            bot_user_id = 'bot'
            if hasattr(ctx.event.query, 'adapter') and hasattr(ctx.event.query.adapter, 'bot_account_id'):
                bot_user_id = ctx.event.query.adapter.bot_account_id

            # Save the bot response record
            await self._save_chat_record(
                user_id=bot_user_id,
                nickname='LangBot',
                message=full_response,
                group_id=event.launcher_id,
                is_bot_message=True,
            )

        except Exception as e:
            self.logger.error(f'Error handling bot response: {e}')

    async def destroy(self):
        """Clean up resources when plugin is destroyed"""
        try:
            if self.engine:
                await self.engine.dispose()
                self.logger.info('Database connection closed')
        except Exception as e:
            self.logger.error(f'Error during plugin cleanup: {e}')
