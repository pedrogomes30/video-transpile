# Arquivos Temporários - VideoTranscriber

## ✅ **Arquivos Removidos do Repositório:**

Removemos todos os arquivos `.spec` porque eles são **gerados automaticamente** pelo script `build.py`.

### **Arquivos .spec**
- São criados pelo `build.py` durante o build
- Contêm configurações específicas do PyInstaller
- São únicos para cada build (Windows, Linux, debug, etc.)
- **Não precisam ser versionados**

## 🔧 **Como Funciona Agora:**

1. **Durante o Build**: `build.py` cria um arquivo `.spec` temporário
2. **PyInstaller executa**: Usa o `.spec` para criar o executável
3. **Após o Build**: O arquivo `.spec` é automaticamente removido

## 📁 **Arquivos Ignorados (.gitignore):**

```
# PyInstaller files
*.spec
*.manifest

# Build directories  
/build
/dist

# Python cache
__pycache__/
*.py[cod]
```

## 🧹 **Script de Limpeza:**

Para limpar arquivos temporários manualmente:
```bash
python clean.py
```

Remove:
- Todos os `.spec`
- Diretórios `build/` e `dist/`
- Cache Python
- Logs temporários

## 🎯 **Benefícios:**

✅ **Repositório Limpo**: Sem arquivos gerados automaticamente
✅ **Flexibilidade**: Cada build gera seu próprio `.spec` 
✅ **Versionamento**: Só código-fonte é versionado
✅ **Builds Frescos**: Sempre usa configurações atualizadas

O repositório agora está muito mais limpo e organizado! 🚀
