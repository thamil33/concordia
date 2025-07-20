as far as lanaguage models, we are using our custom openrouter_model and base_openrouter as well as the wrapper classes (retry, rate limit,) and we can utilize the no_language_model if needed but we have access to free models through openrouter so that generally isn't needed for testing.

there is also a utils.py module in the language model, and we do plan on using local models as well in the future, AS well as we would like to be able to asssign different models to different entitities at some point (which currently doesn't appear to be a feature)

so if you want to deep dive into that module with those points in mind, that would be fine.
