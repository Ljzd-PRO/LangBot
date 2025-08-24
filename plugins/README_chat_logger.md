# Chat Logger Plugin / 聊天记录插件

## English Documentation

### Overview
The Chat Logger Plugin is a comprehensive solution for recording group chat messages and bot responses to a database. It provides flexible configuration options for database backends, group filtering, and message type selection.

### Features
- **Multi-Database Support**: Compatible with SQLite, PostgreSQL, MySQL, and other SQLAlchemy-supported databases
- **Selective Group Logging**: Whitelist/blacklist functionality for targeted group monitoring
- **Bot Message Control**: Option to include or exclude bot's own responses
- **Automatic Schema Management**: Creates necessary database tables automatically
- **Asynchronous Operations**: Non-blocking database operations for optimal performance
- **Comprehensive Logging**: Captures user ID, nickname, message content, timestamp, and group information

### Installation
1. Copy the plugin files to the `plugins/` directory in your LangBot installation:
   - `chat_logger.py` - Main plugin implementation
   - `chat_logger.yaml` - Plugin manifest
   - `chat_logger_config_example.yaml` - Configuration examples

2. Install required dependencies:
   ```bash
   pip install sqlalchemy[asyncio] aiosqlite  # For SQLite (default)
   # OR
   pip install sqlalchemy[asyncio] asyncpg   # For PostgreSQL
   # OR
   pip install sqlalchemy[asyncio] aiomysql  # For MySQL
   ```

3. Add configuration to your main `config.yaml` file (see Configuration section below)

4. Restart LangBot

### Configuration
Add the following configuration to your main `config.yaml` file:

```yaml
plugins:
  chat-logger:
    database_url: "sqlite+aiosqlite:///./chat_logs.db"
    database_name: "langbot_chat"
    include_bot_messages: true
    group_whitelist: []  # Empty means log all groups
    group_blacklist: []  # Exclude specific groups
```

#### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `database_url` | string | `"sqlite+aiosqlite:///./chat_logs.db"` | Database connection URL |
| `database_name` | string | `"langbot_chat"` | Database identifier for logging |
| `include_bot_messages` | boolean | `true` | Whether to record bot responses |
| `group_whitelist` | array | `[]` | List of group IDs to log (empty = all) |
| `group_blacklist` | array | `[]` | List of group IDs to exclude |

#### Database URL Examples
- **SQLite**: `"sqlite+aiosqlite:///./chat_logs.db"`
- **PostgreSQL**: `"postgresql+asyncpg://user:password@host:port/database"`
- **MySQL**: `"mysql+aiomysql://user:password@host:port/database"`

### Database Schema
The plugin automatically creates a `chat_records` table with the following structure:

```sql
CREATE TABLE chat_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    nickname VARCHAR(100),
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    group_id VARCHAR(50) NOT NULL,
    is_bot_message BOOLEAN DEFAULT 0
);
```

### Use Cases
- **Chat Backup**: Preserve important group conversations for future reference
- **Data Analytics**: Analyze group activity patterns and user engagement
- **Compliance**: Meet organizational chat record retention requirements
- **Search Foundation**: Prepare data for future chat history search features
- **Moderation**: Review chat history for community management

### Troubleshooting
1. **Database Connection Issues**: Verify the database URL format and credentials
2. **Permission Errors**: Ensure LangBot has write permissions to the database file/directory
3. **Missing Dependencies**: Install the appropriate database driver (aiosqlite, asyncpg, aiomysql)
4. **Plugin Not Loading**: Check the plugin manifest file and ensure proper YAML syntax

---

## 中文文档

### 概述
聊天记录插件是一个全面的解决方案，用于将群聊消息和机器人回复记录到数据库中。它提供了灵活的配置选项，支持多种数据库后端、群组过滤和消息类型选择。

### 功能特性
- **多数据库支持**: 兼容 SQLite、PostgreSQL、MySQL 和其他 SQLAlchemy 支持的数据库
- **选择性群组记录**: 白名单/黑名单功能，用于定向群组监控
- **机器人消息控制**: 可选择包含或排除机器人自身的回复
- **自动模式管理**: 自动创建必要的数据库表
- **异步操作**: 非阻塞数据库操作，确保最佳性能
- **全面记录**: 捕获用户ID、昵称、消息内容、时间戳和群组信息

### 安装步骤
1. 将插件文件复制到 LangBot 安装目录的 `plugins/` 文件夹中：
   - `chat_logger.py` - 主插件实现
   - `chat_logger.yaml` - 插件清单
   - `chat_logger_config_example.yaml` - 配置示例

2. 安装必要的依赖项：
   ```bash
   pip install sqlalchemy[asyncio] aiosqlite  # SQLite (默认)
   # 或者
   pip install sqlalchemy[asyncio] asyncpg   # PostgreSQL
   # 或者
   pip install sqlalchemy[asyncio] aiomysql  # MySQL
   ```

3. 在主 `config.yaml` 文件中添加配置（参见配置部分）

4. 重启 LangBot

### 配置
在主 `config.yaml` 文件中添加以下配置：

```yaml
plugins:
  chat-logger:
    database_url: "sqlite+aiosqlite:///./chat_logs.db"
    database_name: "langbot_chat"
    include_bot_messages: true
    group_whitelist: []  # 空列表表示记录所有群组
    group_blacklist: []  # 排除特定群组
```

#### 配置选项

| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `database_url` | 字符串 | `"sqlite+aiosqlite:///./chat_logs.db"` | 数据库连接URL |
| `database_name` | 字符串 | `"langbot_chat"` | 用于日志记录的数据库标识符 |
| `include_bot_messages` | 布尔值 | `true` | 是否记录机器人回复 |
| `group_whitelist` | 数组 | `[]` | 要记录的群组ID列表（空=全部） |
| `group_blacklist` | 数组 | `[]` | 要排除的群组ID列表 |

#### 数据库URL示例
- **SQLite**: `"sqlite+aiosqlite:///./chat_logs.db"`
- **PostgreSQL**: `"postgresql+asyncpg://用户名:密码@主机:端口/数据库"`
- **MySQL**: `"mysql+aiomysql://用户名:密码@主机:端口/数据库"`

### 数据库模式
插件会自动创建一个 `chat_records` 表，结构如下：

```sql
CREATE TABLE chat_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    nickname VARCHAR(100),
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    group_id VARCHAR(50) NOT NULL,
    is_bot_message BOOLEAN DEFAULT 0
);
```

### 使用场景
- **聊天备份**: 保存重要的群组对话以供将来参考
- **数据分析**: 分析群组活动模式和用户参与度
- **合规要求**: 满足组织的聊天记录保留要求
- **搜索基础**: 为未来的聊天历史搜索功能准备数据
- **社区管理**: 审查聊天历史以进行社区管理

### 故障排除
1. **数据库连接问题**: 验证数据库URL格式和凭据
2. **权限错误**: 确保 LangBot 对数据库文件/目录具有写权限
3. **缺少依赖项**: 安装适当的数据库驱动程序（aiosqlite、asyncpg、aiomysql）
4. **插件未加载**: 检查插件清单文件并确保正确的YAML语法

### 技术支持
如有任何问题或需要帮助，请访问 [LangBot GitHub 仓库](https://github.com/Ljzd-PRO/LangBot) 提交 Issue 或查看文档。