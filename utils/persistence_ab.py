# Package per salvare e rileggere il file su github
from github import Github
import pickle
import streamlit as st

def upload_file(username,token, df,repository_name, file_path ):#username, token, file_path):
    
    #encoded_df = df.applymap(lambda x: x.encode('utf-8') if isinstance(x, str) else x)
    #encoded_data = pickle.dumps(encoded_df)
    encoded_data = pickle.dumps(df)
    # GitHub authentication
    g = Github(username,token)
    # Get repository
    try:
        repo = g.get_user().get_repo(repository_name)
    except Exception as e:
        st.write("Error accessing repository:", e)
        exit()
    
    try:    
        file = repo.get_contents(file_path)
        repo.update_file(file_path, "Updated data", encoded_data, file.sha)
        #st.write("File updated successfully.")
    except:
        repo.create_file(file_path, 'File created', encoded_data)

def retrieve_file(username, token,repository_name, file_path):#username,token, file_path):
    g = Github(username,token)

    # Get repository
    try:
        repo = g.get_user().get_repo(repository_name)
    except Exception as e:
        st.write("Error accessing repository:", e)
        exit()
    contents = repo.get_contents(file_path)
    content_string = contents.decoded_content
    loaded_data = pickle.loads(content_string)
    
    return loaded_data

def upload_dict(username, token, data, repository_name, file_path):
    encoded_data = pickle.dumps(data)
     # GitHub authentication
    g = Github(username,token)
    # Get repository
    try:
        repo = g.get_user().get_repo(repository_name)
    except Exception as e:
        st.write("Error accessing repository:", e)
        exit()
    try:    
        file = repo.get_contents(file_path)
        repo.update_file(file_path, "Updated data", encoded_data, file.sha)
    except:
        repo.create_file(file_path, 'File created', encoded_data)
