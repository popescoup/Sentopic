"""
LLM CLI Interface

Command-line interface for LLM features including testing, keyword suggestions,
and chat functionality.
"""

import sys
from typing import List, Optional
from ..llm import llm_config, get_llm_provider, get_embedding_provider, is_llm_available


def test_llm_configuration():
    """Test LLM configuration and providers."""
    print("=== LLM Configuration Test ===\n")
    
    # Check if LLM is enabled
    if not llm_config.is_enabled():
        print("❌ LLM features are disabled in configuration")
        print("Set 'enabled': true in the 'llm' section of config.json to enable LLM features")
        return 1
    
    print("✅ LLM features are enabled")
    
    # Validate configuration
    print("\n--- Configuration Validation ---")
    is_valid, errors = llm_config.validate_configuration()
    
    if not is_valid:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  • {error}")
        return 1
    
    print("✅ Configuration validation passed")
    
    # Test available providers
    print("\n--- Provider Testing ---")
    available_providers = llm_config.get_available_providers()
    
    if not available_providers:
        print("❌ No LLM providers are available")
        print("Please check your API keys and provider configuration")
        return 1
    
    print(f"Available providers: {', '.join(available_providers)}")
    
    # Test each provider
    test_results = llm_config.test_providers()
    all_passed = True
    
    for provider_name, (success, message) in test_results.items():
        if success:
            print(f"✅ {provider_name}: {message}")
        else:
            print(f"❌ {provider_name}: {message}")
            all_passed = False
    
    # Test embeddings if enabled
    print("\n--- Embeddings Testing ---")
    if llm_config.is_feature_enabled('rag_search'):
        embedding_provider = get_embedding_provider()
        if embedding_provider:
            try:
                # Test with a simple phrase
                test_response = embedding_provider.generate_embeddings(["test embedding"])
                if test_response.embeddings.size > 0:
                    print(f"✅ Embeddings: {embedding_provider.get_provider_name()} "
                          f"(dimension: {embedding_provider.get_embedding_dimension()})")
                else:
                    print("❌ Embeddings: Failed to generate test embedding")
                    all_passed = False
            except Exception as e:
                print(f"❌ Embeddings: Error - {str(e)}")
                all_passed = False
        else:
            print("❌ Embeddings: Provider not available")
            all_passed = False
    else:
        print("⚠️  Embeddings: Feature disabled in configuration")
    
    # Feature availability summary
    print("\n--- Feature Availability ---")
    features = llm_config.get_feature_config()
    
    for feature_name, is_enabled in features.items():
        status = "✅" if is_enabled else "⚠️"
        enabled_text = "enabled" if is_enabled else "disabled"
        print(f"{status} {feature_name}: {enabled_text}")
    
    # Overall result
    print("\n--- Overall Result ---")
    if all_passed and available_providers:
        print("✅ LLM setup is working correctly!")
        print(f"Default provider: {llm_config.get_default_provider()}")
        return 0
    else:
        print("❌ LLM setup has issues that need to be resolved")
        return 1


def suggest_keywords_interactive():
    """Interactive keyword suggestion."""
    print("=== AI Keyword Suggestion ===\n")
    
    if not llm_config.is_enabled():
        print("❌ LLM features are disabled. Enable them in config.json to use keyword suggestions.")
        return 1
    
    if not llm_config.is_feature_enabled('keyword_suggestion'):
        print("❌ Keyword suggestion feature is disabled in configuration.")
        return 1
    
    # Get user problem description
    print("Describe what you want to research or analyze:")
    print("Example: 'I want to analyze sentiment about iPhone battery life issues'")
    print()
    
    problem_description = input("Your research goal: ").strip()
    
    if not problem_description:
        print("❌ Please provide a description of what you want to research.")
        return 1
    
    print(f"\n🤖 Generating keyword suggestions for: '{problem_description}'")
    print("⏳ This may take a few seconds...")
    
    try:
        # Get LLM provider
        provider = get_llm_provider()
        if not provider:
            print("❌ No LLM provider available. Please check your configuration.")
            return 1
        
        # Create a simple keyword suggestion prompt
        system_prompt = """You are a helpful assistant that suggests relevant keywords for analyzing Reddit discussions. 
Given a research goal or topic, suggest 5-10 specific keywords that would be effective for finding relevant posts and comments.

Guidelines:
- Include both exact phrases and related terms
- Consider common abbreviations and slang
- Think about how people actually discuss this topic on Reddit
- Include both positive and negative aspects
- Suggest keywords that are specific enough to be meaningful

Return only the keywords, separated by commas, with no additional explanation."""
        
        user_prompt = f"Research goal: {problem_description}\n\nSuggest relevant keywords for Reddit analysis:"
        
        # Generate keywords
        response = provider.generate(user_prompt, system_prompt)
        
        if response.content:
            keywords = [kw.strip().strip('"\'') for kw in response.content.split(',')]
            keywords = [kw for kw in keywords if kw]  # Remove empty strings
            
            print(f"\n✅ Suggested keywords ({len(keywords)} found):")
            for i, keyword in enumerate(keywords, 1):
                print(f"  {i}. {keyword}")
            
            print(f"\n💰 Token usage: {response.tokens_used} tokens")
            print(f"💰 Estimated cost: ${response.cost_estimate:.4f}")
            print(f"🤖 Provider: {response.provider} ({response.model})")
            
            # Offer to copy for analysis
            print("\n📋 You can copy these keywords to use in your analysis:")
            print(", ".join(keywords))
            
        else:
            print("❌ No keywords were generated. Please try rephrasing your research goal.")
            return 1
    
    except Exception as e:
        print(f"❌ Error generating keywords: {str(e)}")
        return 1
    
    return 0


def suggest_keywords_direct(problem_description: str):
    """Direct keyword suggestion from command line argument."""
    if not llm_config.is_enabled():
        print("❌ LLM features are disabled.")
        return 1
    
    if not llm_config.is_feature_enabled('keyword_suggestion'):
        print("❌ Keyword suggestion feature is disabled.")
        return 1
    
    try:
        provider = get_llm_provider()
        if not provider:
            print("❌ No LLM provider available.")
            return 1
        
        system_prompt = """You are a helpful assistant that suggests relevant keywords for analyzing Reddit discussions. 
Given a research goal or topic, suggest 5-10 specific keywords that would be effective for finding relevant posts and comments.

Return only the keywords, separated by commas, with no additional explanation."""
        
        user_prompt = f"Research goal: {problem_description}\n\nSuggest relevant keywords for Reddit analysis:"
        
        response = provider.generate(user_prompt, system_prompt)
        
        if response.content:
            keywords = [kw.strip().strip('"\'') for kw in response.content.split(',')]
            keywords = [kw for kw in keywords if kw]
            
            print(", ".join(keywords))
        else:
            print("No keywords generated")
            return 1
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


def show_llm_status():
    """Show current LLM status and configuration."""
    print("=== LLM Status ===\n")
    
    # Basic status
    if llm_config.is_enabled():
        print("✅ LLM features: ENABLED")
    else:
        print("❌ LLM features: DISABLED")
        return
    
    # Available providers
    providers = llm_config.get_available_providers()
    print(f"🔧 Available providers: {', '.join(providers) if providers else 'None'}")
    
    # Default provider
    default = llm_config.get_default_provider()
    print(f"🎯 Default provider: {default}")
    
    # Features
    features = llm_config.get_feature_config()
    enabled_features = [name for name, enabled in features.items() if enabled]
    print(f"⚡ Enabled features: {', '.join(enabled_features)}")
    
    # Embeddings
    embeddings_config = llm_config.get_embeddings_config()
    if embeddings_config:
        provider = embeddings_config.get('provider', 'unknown')
        model = embeddings_config.get('model', 'unknown')
        print(f"🔍 Embeddings: {provider} ({model})")
    
    # Usage summary
    usage = llm_config.get_usage_summary()
    if usage:
        print("\n💰 Usage Summary:")
        for provider_name, stats in usage.items():
            print(f"  {provider_name}: {stats['total_tokens_used']} tokens, ${stats['total_cost_estimate']:.4f}")


def handle_llm_commands(args: List[str]) -> int:
    """
    Handle LLM-related CLI commands.
    
    Args:
        args: List of command-line arguments (excluding the program name)
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if not args:
        print("Error: LLM command required")
        return 1
    
    command = args[0]
    
    if command == "--test-llm":
        return test_llm_configuration()
    
    elif command == "--suggest-keywords":
        if len(args) > 1:
            # Direct mode with problem description
            problem_description = " ".join(args[1:])
            return suggest_keywords_direct(problem_description)
        else:
            # Interactive mode
            return suggest_keywords_interactive()
    
    elif command == "--llm-status":
        show_llm_status()
        return 0
    
    else:
        print(f"Unknown LLM command: {command}")
        return 1