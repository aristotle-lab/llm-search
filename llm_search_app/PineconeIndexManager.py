from pinecone import Pinecone, ServerlessSpec

class PineconeIndexManager:
  def __init__(self, api_key: str, index_name: str, dimension: int, cloud: str, region: str):
    self.api_key = api_key
    self.index_name = index_name
    self.dimension = dimension
    self.cloud = cloud
    self.region = region
    self.pc = self._initialize_pinecone()

  def _initialize_pinecone(self):
    if not self.api_key:
      raise ValueError("PINECONE_API_KEY environment variable is not set")
    return Pinecone(api_key=self.api_key)

  def create_or_connect_index(self):
    if self.index_name not in self.pc.list_indexes():
      self.pc.create_index(
        name=self.index_name,
        dimension=self.dimension,
        spec=ServerlessSpec(
          cloud=self.cloud,
          region=self.region
        )
      )
    return self.pc.Index(self.index_name)

# # Usage
# api_key = os.getenv("PINECONE_API_KEY")
# index_manager = PineconeIndexManager(
#   api_key=api_key,
#   index_name="github-issues",
#   dimension=1536,
#   cloud="aws",
#   region="us-east-1"
# )
# index = index_manager.create_or_connect_index()