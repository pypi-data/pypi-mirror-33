# Flask-JWT-RFC7519
[![Build Status](https://travis-ci.com/Groenbech96/flask-jwt-rfc7519.svg?token=DE2K5YMdyk9RyqU7uyEo&branch=master)](https://travis-ci.com/Groenbech96/flask-jwt-rfc7519)

### This Repository is build on [flask-jwt-extended](https://github.com/vimalloc/flask-jwt-extended). All credit for the framework goes to the owner of the flask-jwt-extended repository.

This implementation changes the jwt payload to follow the proposed standard of RFC7519. This includes sub, aud and iss claims.

Differences between [flask-jwt-extended](https://github.com/vimalloc/flask-jwt-extended) and this repo:

Added two config options. You can specify what who the ISS is and who the AUD is.

```current_app.config['JWT_ISS_CLAIM'] (string)``` 
```current_app.config['JWT_AUD_CLAIM'] (list of strings)```

The SUB is handled by the `current_app.config['JWT_IDENTITY_CLAIM']` already in the flask-jwt-extended

To verify the AUD and/or ISS claim use respectively:

```@jwt.aud_claim_verification_loader```
```@jwt.iss_claim_verification_loader```

They will provide the value from key-value pair in the config dict. 
To handle incorrect aud or iss use the 

```@jwt.aud_claim_verification_failed_loader```
```@jwt.iss_claim_verification_failed_loader```

The user_claims_loader is removed and replaced with additional_claims_loader.

