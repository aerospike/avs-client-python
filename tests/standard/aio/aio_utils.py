async def drop_specified_index(admin_client, namespace, name):
    await admin_client.index_drop(namespace=namespace, name=name)
