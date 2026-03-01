from service.database.service import DatabaseService
from service.plugin.registry import PluginRegistry


async def create_database_service(
    plugin_name: str = "sqlite",
    **backend_options,
) -> DatabaseService:
    """
    按插件名称创建数据库服务

    默认使用 sqlite 插件
    """
    registry = PluginRegistry()
    registry.load()

    plugin = registry.get_database_plugin(plugin_name)
    if plugin is None:
        raise LookupError(f"数据库插件不存在: {plugin_name}")

    backend = plugin.create_backend(**backend_options)
    await plugin.setup(backend)
    return DatabaseService(backend)
