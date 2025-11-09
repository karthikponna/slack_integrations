from pymongo import MongoClient

from src.slack_integrations_online.config import settings

def get_single_document(url: str) -> str:

    try:
        client = MongoClient(settings.MONGODB_URI)  # Adjust based on your settings
        db = client[settings.MONGODB_DATABASE_NAME]  # Adjust based on your database name
        collection = db['raw']


        document = collection.find_one({"metadata.url": url})
                
        if not document:
            return f"<error>No document found with URL: {url}</error>"

        # Extract content and URL from the document
        content = document.get('content', '')
        doc_url = document.get('metadata', {}).get('url', url)

        # Format the result in XML structure
        result = f"""
        <document>
        <url>{doc_url}</url>
        <content>{content.strip()}</content>
        </document>
        """

        return result

    except Exception as e:
        return f"<error>Error retrieving document: {str(e)}</error>"
    
    finally:
        if 'client' in locals():
            client.close()
