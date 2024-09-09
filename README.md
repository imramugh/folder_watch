## Folder Watch

Folder watch is a utility that monitors a folder the contains documents.  When new files are added to the folder, or existing files are modified, the underlying SQL Lite DB table is updated.  I intend build on this to have an embedding utility scan the database to populate a queue that will feed an vector embedding process.  Ultimately, the goal is to have a RAG pipeline.
