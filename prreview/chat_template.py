from langchain_core.prompts import ChatPromptTemplate

file_review_template = ChatPromptTemplate.from_template(
    """
    You are a code review assistant designed to analyze a pull request.
            The contents of each modified file will be provided, along with the issue description.
            Analyze each file and provide feedback on the code quality and potential issues.
            
            Provide the suggestions in the JSON list format where each item contains:
            1. the function/method/class name, or line number (key 'ref')
            2. the suggestion (key 'suggestion')
            
            Provide only the JSON as output in the response.
            
            Issue description:
            
            {issue}
            
            Pylint analysis:
            
            {pylint_output}
            
            Modified file:
            
            {file_contents}
            """
)

file_refactor_template = ChatPromptTemplate.from_template(
    """
    Given a source code Python file, apply the suggestions given in the JSON format and rewrite the source code 
    file. Only provide the modified source code file as output in the response.
    
    If there are no suggestions, return the original file.
    
    --------------------------------------------
    Suggestions:
    
    {suggestions}
    --------------------------------------------
    
    Original file:
    
    ```
    {file_contents}
    ```
    """
)
