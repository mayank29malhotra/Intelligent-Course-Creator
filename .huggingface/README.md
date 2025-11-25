# Hugging Face Spaces Configuration

This Space hosts the **Intelligent Course Creator** - an AI-powered course generation system using Google Gemini.

## Required Secrets

Add these in your Space Settings → Repository secrets:

### 1. GEMINI_API_KEY (Required)
Your Google Gemini API key for course generation.

**How to get it:**
1. Visit https://ai.google.dev/
2. Click "Get API key"
3. Create or select a project
4. Copy your API key
5. Add to HF Spaces Secrets as `GEMINI_API_KEY`

## Space Configuration

The app automatically detects when running in HF Spaces via the `SPACE_ID` environment variable and configures itself accordingly:

- **Server**: Binds to `0.0.0.0:7860` (required for HF Spaces)
- **Share**: Automatically set to `True` for public access
- **Gradio SDK**: Version 5.0.0

## Hardware Requirements

- **Minimum**: CPU Basic (2 vCPU, 16GB RAM)
- **Recommended**: CPU Upgrade (4 vCPU, 32GB RAM) for faster generation
- **GPU**: Not required (uses Gemini API)

## Rate Limits

The free tier of Gemini API has usage limits. The app includes:
- 30-second delays between agent calls
- Automatic retry with exponential backoff
- Progress tracking to show generation status

## Expected Performance

- **Course Generation Time**: 10-15 minutes
- **API Calls per Course**: ~15-20 requests
- **Memory Usage**: ~2-4GB during generation

## Troubleshooting

### "API key not found"
- Verify `GEMINI_API_KEY` is set in Secrets
- Restart the Space after adding secrets
- Check the key is valid at https://ai.google.dev/

### "Rate limit exceeded"
- Wait 1 minute and try again
- Consider upgrading to paid Gemini tier
- Reduce course duration (hours parameter)

### "Space not loading"
- Check build logs for errors
- Verify all dependencies in requirements.txt
- Restart the Space from Settings

## Privacy & Security

- **API Keys**: Stored securely in HF Secrets (not in code)
- **User Data**: Not stored or logged
- **Generated Content**: Temporary (not persisted)
- **DOCX Downloads**: Generated on-demand, not saved

## Support

For issues specific to this Space:
1. Check the [DEPLOYMENT_FIX_SUMMARY.md](../DEPLOYMENT_FIX_SUMMARY.md)
2. Review [README.md](../README.md) for usage instructions
3. Check build logs in Space Settings

---

**Space Status**: ✅ Production Ready  
**Last Updated**: 2025-01-25  
**Gradio Version**: 5.0.0  
**Python Version**: 3.10+
