"""A valid set of production environment variables, shared by the settings tests."""
VALID = {
    "SECRET_KEY": "q7Zr!m2Xv9Lp4Tn8Wc1Ys6Hd3Fg5Jk0Bb-Ua_Ei+Ro=Mx2Nz7Vt4Sq9Pl",
    "JWT_SIGNING_KEY": "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2W3x4Y5z6-ab",
    "ALLOWED_HOSTS": "api.example.com, www.example.com",
    "CORS_ALLOWED_ORIGINS": "https://app.example.com",
    "CSRF_TRUSTED_ORIGINS": "https://api.example.com",
}
