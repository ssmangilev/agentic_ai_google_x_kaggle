async def auto_save_to_memory_callback(callback_context):
    """Callback to save the current session to long-term memory."""
    session = callback_context._invocation_context.session
    # Assuming 'runner' instance is available or accessible
    await runner.memory_service.add_session_to_memory(session)