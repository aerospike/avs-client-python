import asyncio


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


async def wait_for_index(admin_client, namespace: str, index: str):
    
    verticies = 0
    unmerged_recs = 0
    
    while verticies == 0 or unmerged_recs > 0:
        status = await admin_client.index_get_status(
            namespace=namespace,
            name=index,
        )

        verticies = status.index_healer_vertices_valid
        unmerged_recs = status.unmerged_record_count

        # print(verticies)
        # print(unmerged_recs)
        await asyncio.sleep(0.5)