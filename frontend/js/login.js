const API = 'http://127.0.0.1:8000'

const formLogin = document.getElementById('form-login')

// Função auxiliar para gerar o hash SHA-256 de forma automática e nativa
async function gerarHashSHA256(texto) {
  const encoder = new TextEncoder()
  const data = encoder.encode(texto)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

formLogin.addEventListener('submit', async (e) => {
  e.preventDefault()

  const senhaPura = document.getElementById('senha').value

  // Gera o hash automaticamente antes de montar o objeto de envio
  const senhaCriptografada = await gerarHashSHA256(senhaPura)

  const dados = {
    email: document.getElementById('email').value,
    senha: senhaCriptografada // <-- Envia o hash para a API validar
  }

  // Faz a chamada para a rota oficial de login
  const resposta = await fetch(`${API}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados)
  })

  const resultado = await resposta.json()

  if (resposta.ok) {
    localStorage.setItem('token', resultado.access_token)   // guarda o token na "gaveta"
    window.location.href = 'dashboard.html'
  } else {
    // Alinhado com a mensagem padrão de erro retornada pela sua API
    alert(resultado.detail || 'E-mail ou senha incorretos.')
  }
})
