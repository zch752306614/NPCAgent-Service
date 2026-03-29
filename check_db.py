import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("story_nodes")

print("向量数据库中的所有节点：")
results = collection.get()
print(f"节点ID: {results['ids']}")
print(f"节点数量: {len(results['ids'])}")

print("\n节点详细信息：")
for i, node_id in enumerate(results['ids']):
    metadata = results['metadatas'][i]
    document = results['documents'][i]
    print(f"\n节点ID: {node_id}")
    print(f"节点类型: {metadata.get('节点类型', '')}")
    print(f"前置条件: {metadata.get('前置条件', '')}")
    print(f"触发关键词: {metadata.get('触发关键词', '')}")
    print(f"文档内容: {document[:100]}...")
