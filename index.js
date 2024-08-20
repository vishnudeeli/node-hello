const { SecretClient } = require("@azure/keyvault-secrets");
const { DefaultAzureCredential } = require("@azure/identity");

const keyVaultName = "msbpro-kv-prod-01";
const secretName = "myname";

const credential = new DefaultAzureCredential();
const client = new SecretClient(`https://${keyVaultName}.vault.azure.net`, credential);

const secret = await client.getSecret(secretName);
const secretValue = secret.value;


const http = require('http');
const port = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  const msg = 'Hello Node!\n'+secretValue
  res.end(msg);
});

server.listen(port, () => {
  console.log(`Server running on http://localhost:${port}/`);
});
