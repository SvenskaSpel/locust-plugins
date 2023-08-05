def __getattr__(name: str):
    if name.endswith("User"):
        raise ImportError(
            f"locust_plugins.users no longer re-exports users. Use locust_plugins.users.{name.replace('User', '').lower()}.{name} instead"
        )
    raise ImportError(f"cannot import name '{name}' from 'locust_plugins.users'")
