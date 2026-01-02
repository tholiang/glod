# Allowed Directories Persistence

## Overview

The client maintains a persistent list of allowed directories that survives server restarts. This allows you to add directories once and have them automatically re-synced to the server when it restarts.

## How It Works

### Storage

- Allowed directories are stored in `~/.glod_allowed_dirs` as a JSON file
- The file contains a simple structure:
  ```json
  {
    "allowed_dirs": ["/path/to/dir1", "/path/to/dir2"]
  }
  ```

### Client-Side

1. **On Startup**: `AgentClient` loads the list from `~/.glod_allowed_dirs`
2. **When Adding**: `/allow <path>` command adds to both memory and disk
3. **On Server Restart**: `sync_allowed_dirs()` resends all directories to the server

### Server-Side

- The server remains **stateless** with no persistence
- All allowed directories are in-memory in the `App` instance
- Lost on restart (but client resends them)

### Automatic Cleanup

- Non-existent paths are automatically filtered out when loading
- If you delete a directory on disk, it's removed from the allowlist on next client restart

## Flow Example

```
1. User: /allow /projects/myapp
   → Client adds to memory and ~/.glod_allowed_dirs
   → Server adds to in-memory App instance

2. User: /server restart
   → Server stops and starts (clears memory)
   → Client calls sync_allowed_dirs()
   → /projects/myapp is re-sent to server
   → Server adds back to in-memory App instance

3. All allowed directories are available again
```

## Usage

```
# Add a directory
/allow /path/to/project

# Restart server (directories are preserved)
/server restart

# Directories are automatically re-added to the restarted server
```

