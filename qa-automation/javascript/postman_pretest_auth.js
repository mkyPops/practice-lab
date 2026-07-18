/**
 * Postman pre-request script: Auth Token Manager
 *
 * Ensures every outgoing request carries a valid Bearer token.
 * Caches the token (and its expiry) in collection variables so it is
 * only refreshed when missing or expired, avoiding an auth call on
 * every single request.
 *
 * Required collection/environment variables:
 *   - auth_url            Token endpoint (OAuth2 client_credentials style)
 *   - auth_client_id
 *   - auth_client_secret
 *
 * Managed automatically by this script:
 *   - access_token
 *   - access_token_expiry (epoch ms)
 */

const authUrl = pm.collectionVariables.get('auth_url');
const clientId = pm.collectionVariables.get('auth_client_id');
const clientSecret = pm.collectionVariables.get('auth_client_secret');

const cachedToken = pm.collectionVariables.get('access_token');
const cachedExpiry = parseInt(pm.collectionVariables.get('access_token_expiry'), 10) || 0;

// 30s safety buffer so we refresh slightly before actual expiry
const isExpired = Date.now() > (cachedExpiry - 30000);

function applyToken(token) {
    pm.request.headers.upsert({
        key: 'Authorization',
        value: `Bearer ${token}`
    });
}

if (cachedToken && !isExpired) {
    applyToken(cachedToken);
} else {
    const tokenRequest = {
        url: authUrl,
        method: 'POST',
        header: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: {
            mode: 'urlencoded',
            urlencoded: [
                { key: 'grant_type', value: 'client_credentials' },
                { key: 'client_id', value: clientId },
                { key: 'client_secret', value: clientSecret }
            ]
        }
    };

    // Synchronous-style handling via pm.sendRequest's callback;
    // Postman pauses script execution until this resolves.
    pm.sendRequest(tokenRequest, (err, res) => {
        if (err) {
            throw new Error(`Auth token request failed: ${err.message}`);
        }

        const body = res.json();
        if (!body.access_token) {
            throw new Error('Auth response did not contain access_token');
        }

        const expiryTimestamp = Date.now() + (body.expires_in * 1000);

        pm.collectionVariables.set('access_token', body.access_token);
        pm.collectionVariables.set('access_token_expiry', expiryTimestamp.toString());

        applyToken(body.access_token);
    });
}
