# AVISO DE SEGURANÇA / SECURITY NOTICE

## 🔐 Credenciais Z-API / Z-API Credentials

**IMPORTANTE:** As credenciais Z-API fornecidas nos arquivos originais foram removidas do código-fonte por questões de segurança.

**IMPORTANT:** The Z-API credentials provided in the original files have been removed from the source code for security reasons.

### ✅ Ação Requerida / Action Required

As credenciais Z-API agora devem ser configuradas como variáveis de ambiente:

Z-API credentials must now be configured as environment variables:

- `Z_API_INSTANCE` - ID da instância Z-API / Z-API instance ID
- `Z_API_TOKEN` - Token de autenticação / Authentication token

### 🔄 Recomendação de Rotação / Rotation Recommendation

**CRÍTICO:** Se as credenciais anteriores foram expostas publicamente, recomendamos fortemente:

**CRITICAL:** If the previous credentials were publicly exposed, we strongly recommend:

1. Rotacionar (regenerar) as credenciais na plataforma Z-API
2. Atualizar as variáveis de ambiente com as novas credenciais
3. Verificar logs de acesso à conta Z-API para atividades suspeitas

---

1. Rotate (regenerate) the credentials on the Z-API platform
2. Update environment variables with new credentials  
3. Check Z-API account access logs for suspicious activity

### 📋 Arquivos Removidos / Removed Files

Os seguintes arquivos contendo credenciais foram removidos:

The following files containing credentials have been removed:

- `attached_assets/Pasted-https-api-z-api-io-instances-*-token-*.txt`

### ✅ Status Atual / Current Status

✓ Credenciais movidas para variáveis de ambiente seguras
✓ Validação implementada para garantir que credenciais estejam configuradas
✓ Sistema não iniciará sem credenciais válidas
✓ Arquivo com credenciais expostas foi removido do repositório

---

✓ Credentials moved to secure environment variables
✓ Validation implemented to ensure credentials are configured
✓ System will not start without valid credentials
✓ File with exposed credentials removed from repository

### 🛡️ Melhores Práticas / Best Practices

1. **NUNCA** commite credenciais em código-fonte
2. Use sempre variáveis de ambiente ou gestores de secrets
3. Rotacione credenciais regularmente
4. Monitore acessos e uso de APIs

---

1. **NEVER** commit credentials to source code
2. Always use environment variables or secret managers
3. Rotate credentials regularly
4. Monitor access and API usage
