async def drop_specified_index(admin_client, namespace, name):
    await admin_client.index_drop(namespace=namespace, name=name)

def gen_records(count: int, vec_bin: str, vec_dim: int):
    num = 0
    while num < count:
        key_and_rec = (
            num,
            { "id": num, vec_bin: [float(num)] * vec_dim}
        )
        yield key_and_rec
        num += 1
