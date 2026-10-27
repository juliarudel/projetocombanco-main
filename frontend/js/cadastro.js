const API = 'http://127.0.0.1:8000'
protegerPagina()
const formCadastro = document.getElementById('form-cadastro')

formCadastro.addEventListener('submit', async (e) => {
  e.preventDefault()

  const usuario = {
    nome: document.getElementById('nome').value,
    email: document.getElementById('email').value,
    senha: document.getElementById('senha').value
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
