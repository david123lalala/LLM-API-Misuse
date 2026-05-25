import os
import javalang
import json

# List of common crypto-related classes
crypto_apis = []

def uses_crypto_api(method_node):
    """Check if the method body contains any crypto API usage."""
    if hasattr(method_node, 'body') and method_node.body:
        method_body = method_node.body
        if isinstance(method_body, list):
            method_body = " ".join(str(stmt) for stmt in method_body)
        for api in crypto_apis:
            if api in method_body:
                return True
    return False

def parse_java_file(file_path):
    """Parse the Java file to extract class and method information."""
    with open(file_path, 'r', encoding='utf-8') as file:
        java_code = file.read()

    try:
        tree = javalang.parse.parse(java_code)
    except javalang.parser.JavaSyntaxError:
        print(f"Syntax error in {file_path}, skipping.")
        return None

    classes_info = {}
    
    for _, class_node in tree.filter(javalang.tree.ClassDeclaration):
        class_name = class_node.name
        class_methods = {}
        static_variables = {}

        for member in class_node.body:
            if isinstance(member, javalang.tree.MethodDeclaration):
                class_methods[member.name] = member  
            elif isinstance(member, javalang.tree.FieldDeclaration):
                for declarator in member.declarators:
                    var_name = declarator.name
                    if declarator.initializer is not None:
                        var_value = str(declarator.initializer)  
                    else:
                        var_value = None  
                    static_variables[var_name] = var_value

        classes_info[class_name] = {
            "methods": class_methods,
            "static_variables": static_variables
        }
    
    return classes_info

def analyze_functions(classes_info):
    """Analyze methods in classes for classification into slices A, B, and C."""
    slice_A = [] 
    slice_B = []  
    function_calls = []

    # Classify functions
    for class_name, info in classes_info.items():
        for method_name, method_info in info['methods'].items():
            if uses_crypto_api(method_info):
                slice_A.append(f"{class_name}.{method_name}")
            else:
                slice_B.append(f"{class_name}.{method_name}")

    slice_C = []
    for b_method in slice_B:

        slice_C.append(b_method)  # This is just a placeholder

    return slice_A, slice_B, slice_C

def extract_function_calls(classes_info):
    """Extract internal function calls between methods."""
    function_calls = []
    
    for class_name, info in classes_info.items():
        methods = info['methods']
        for method_name, method_info in methods.items():
            # Extract method invocations
            if hasattr(method_info, 'body') and method_info.body:
                for _, invocation in method_info.filter(javalang.tree.MethodInvocation):
                    function_calls.append({
                        "from": f"{class_name}.{method_name}",
                        "to": invocation.member
                    })

    return function_calls

def analyze_java_files(crypto_file_paths):
    """Analyze each Java file for functions and static variables."""
    analysis_results = []

    for file_path in crypto_file_paths:
        print(f"Analyzing {file_path}...")
        classes_info = parse_java_file(file_path)

        if classes_info is None:
            continue

        slice_A, slice_B, slice_C = analyze_functions(classes_info)
        function_calls = extract_function_calls(classes_info)

        # Create analysis result for this file
        analysis_results.append({
            "file_path": file_path,
            "slice_A": slice_A,
            "slice_B": slice_B,
            "slice_C": slice_C,
            "function_calls": function_calls,
            "static_variables": classes_info[list(classes_info.keys())[0]]["static_variables"]
        })

    return analysis_results

def save_results_to_json(results, output_path):
    """Save the analysis results to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Results saved to {output_path}")

# Example usage
json_data = {
}


file_path_list=[]

save_path_list=[]

for file_path,output_path in zip(file_path_list,save_path_list):
    with open(file_path,'r') as file:
        json_data=json.load(file)

    # Load file paths and analyze
    crypto_file_paths = json_data["crypto_file_paths"]
    results = analyze_java_files(crypto_file_paths)

    # Save the analysis results
    save_results_to_json(results, output_path)
