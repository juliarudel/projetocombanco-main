const API = 'http://127.0.0.1:8000'
protegerPagina()
const formCadastro = document.getElementById('form-cadastro')

// Função auxiliar para gerar o hash SHA-256 de forma automática e nativa
async function gerarHashSHA256(texto) {
  const encoder = new TextEncoder()
  const data = encoder.encode(texto)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

formCadastro.addEventListener('submit', async (e) => {
  e.preventDefault()

  const senhaPura = document.getElementById('senha').value

  // Gera o hash automaticamente antes de montar o objeto que vai para a API
  const senhaCriptografada = await gerarHashSHA256(senhaPura)

  const usuario = {
    nome: document.getElementById('nome').value,
    email: document.getElementById('email').value,
    senha: senhaCriptografada // <-- Agora a senha vai criptografada para o banco
  }

  let resposta
  try {
    resposta = await fetchAutenticado(`${API}/usuarios`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(usuario)
    })
  } catch (erro) {
    alert('Não foi possível conectar à API. Confira se o servidor está rodando em http://127.0.0.1:8000.')
    return
  }

  if (resposta.ok) {
    alert('Cadastro feito com sucesso!')
    window.location.href = 'dashboard.html'
  } else {
    const erro = await resposta.json().catch(() => null)
    alert('Erro ao cadastrar: ' + (erro?.detail || JSON.stringify(erro) || `HTTP ${resposta.status}`))
  }
})
