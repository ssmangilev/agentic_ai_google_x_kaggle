def sanitize_agent_tools(agent):
    """
    Recursively cleans agent tools to remove 'additional_properties' fields
    that cause 400 INVALID_ARGUMENT errors with the Gemini API.
    Handles nested schemas, Unions (oneOf/anyOf), and Arrays.
    """
    if not agent:
        return

    # Helper to clean a schema object (dict or Schema type)
    def _clean_schema(node):
        if node is None:
            return

        # 1. Clean 'additional_properties' if present
        # Handle Dicts
        if isinstance(node, dict):
            node.pop('additional_properties', None)
            node.pop('additionalProperties', None)
        # Handle Objects (Schema types)
        else:
            if hasattr(node, 'additional_properties'):
                try:
                    setattr(node, 'additional_properties', None)
                except Exception:
                    pass
            if hasattr(node, 'additionalProperties'):
                try:
                    setattr(node, 'additionalProperties', None)
                except Exception:
                    pass

        # 2. Recurse into 'properties' (Map of schemas)
        props = None
        if isinstance(node, dict):
            props = node.get('properties')
        elif hasattr(node, 'properties'):
            props = node.properties

        if props and isinstance(props, dict):
            for prop in props.values():
                _clean_schema(prop)

        # 3. Recurse into 'items' (Array schemas)
        items = None
        if isinstance(node, dict):
            items = node.get('items')
        elif hasattr(node, 'items'):
            items = node.items

        if items:
            _clean_schema(items)

        # 4. Recurse into 'allOf', 'anyOf', 'oneOf' (Union schemas)
        # This is often where Pydantic Optional/Union
        # types hide the forbidden field
        for key in ['allOf', 'anyOf', 'oneOf']:
            lst = None
            if isinstance(node, dict):
                lst = node.get(key)
            elif hasattr(node, key):
                lst = getattr(node, key)

            if isinstance(lst, list):
                for item in lst:
                    _clean_schema(item)

    # Walk through tools of the current agent
    # We use getattr to safely access tools if they exist
    tools = getattr(agent, 'tools', []) or []

    for tool in tools:
        # Tool objects usually have 'function_declarations'
        funcs = getattr(tool, 'function_declarations', []) or []
        for func in funcs:
            # FunctionDeclaration has 'parameters' (Schema)
            params = getattr(func, 'parameters', None)
            if params:
                _clean_schema(params)

    # Recursively clean sub-agents (for Pipelines/SequentialAgents)
    sub_agents = getattr(agent, 'sub_agents', []) or []
    for sub in sub_agents:
        sanitize_agent_tools(sub)
