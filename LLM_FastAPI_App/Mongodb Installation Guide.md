- In the terminal(macOS), use brew to install mongodb
    - brew tap mongodb/brew
    - brew install mongodb-community

- Install pymongo using
    - pip install pymongo


- Add the data directory
    - mongod --dbpath /path/to/your/data/directory

    - This will start the MongoDB server process. The data files willl be
    stored inside the specified directory. This directory must be created before running the commansd
    
    - Once we run this command MoongoDB will listen to the connection url we provided,
    
    - Inside the db_directory, you can see various files. Some with .wt extension, .lock etc
    
     - Example: 
       - The collections**.wt contains metadata info about the collections
         - For example, it has info about the chat_history collections in this usecase
       - The index-**.wt will be for the indeices that are created. Indeces are created for some fields in
         MongoDB to enable fast retrival. For example, imagine you have chat histortories of 200000 users and everytime
         searching a user by thier user_id or username can be time consuming. So we create an index for the user_id or user_name
         through which we can search faster. Generally, each index you create corresponds to one or more index-*.wt files.
     - Indexes are stored separately from the actual document data. This is crucial for performance. When you query using an indexed field, MongoDB can quickly look up the relevant documents in the index without having to scan the entire collection.
     

Now we can use pymongo to connect to the Mongodb

