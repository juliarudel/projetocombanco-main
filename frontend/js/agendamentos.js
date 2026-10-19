const API = 'http://127.0.0.1:8000';

const formAgendamento = document.getElementById('form-agendamento');
const botaoSubmit = document.getElementById('btn-submit-agendamento');
const blocoStatus = document.getElementById('bloco-status');
const corpoTabela = document.getElementById('corpo-tabela');

let agendamentosCarregados = [];

// Converte horários como 73800 para 20:30, se necessário.
function formatarHora(valor) {
  if (valor === null || valor === undefined || valor === '') return '';

  const texto = String(valor);

  if (texto.includes(':')) {
    const partes = texto.split(':');
    return `${partes[0].padStart(2, '0')}:${partes[1].padStart(2, '0')}`;
  }

  const segundos = Number(valor);

  if (!Number.isFinite(segundos)) return '';

  const horas = Math.floor(segundos / 3600);
  const minutos = Math.floor((segundos % 3600) / 60);

  return `${String(horas).padStart(2, '0')}:${String(minutos).padStart(2, '0')}`;
}

async function verificarResposta(resposta) {
  if (!resposta.ok) {
    const erro = await resposta.text();
    throw new Error(`Erro ${resposta.status}: ${erro}`);
  }

  return resposta;
}

async function carregarClientes() {
  const resposta = await verificarResposta(
    await fetch(`${API}/clientes`)
  );

  const clientes = await resposta.json();
  const select = document.getElementById('idcliente');

  select.innerHTML = '<option value="">Cliente...</option>';

  clientes.forEach(c => {
    const opcao = document.createElement('option');
    opcao.value = c.idcliente;
    opcao.textContent = c.nome;
    select.appendChild(opcao);
  });
}

async function carregarTatuadores() {
  const resposta = await verificarResposta(
    await fetch(`${API}/tatuadores`)
  );

  const tatuadores = await resposta.json();
  const select = document.getElementById('idtatuador');

  select.innerHTML = '<option value="">Tatuador...</option>';

  tatuadores.forEach(t => {
    const opcao = document.createElement('option');
    opcao.value = t.idtatuador;
    opcao.textContent = t.nometatuador;
    select.appendChild(opcao);
  });
}

function limparFormulario() {
  formAgendamento.reset();
  delete formAgendamento.dataset.idAgendamento;

  botaoSubmit.textContent = 'Cadastrar';
  botaoSubmit.classList.remove('btn-success');
  botaoSubmit.classList.add('btn-primary');

  blocoStatus.style.display = 'none';
}

// ─── PARTE 7: LISTAR AGENDAMENTOS COM EXIBIÇÃO DE MINIATURA ATUALIZADA ───
async function listarAgendamentos() {
  const resposta = await fetch(`${API}/agendamentos`);
  const agendamentos = await resposta.json();

  const corpo = document.getElementById('corpo-tabela');
  corpo.innerHTML = '';

  agendamentos.forEach(a => {
    // encodeURIComponent trata espaços em branco e caracteres especiais no nome do arquivo
    const imagemHtml = a.desenhoaprovado
      ? `<img src="${API}/uploads/${encodeURIComponent(a.desenhoaprovado)}" style="max-width: 60px; max-height: 60px; object-fit: cover; border-radius: 4px;" alt="Desenho">`
      : '-';

    corpo.innerHTML += `
      <tr>
        <td>${a.idagendamento}</td>
        <td>${a.cliente}</td>
        <td>${a.tatuador}</td>
        <td>${String(a.dataagendamento).slice(0, 10)}</td>
        <td>${formatarHora(a.horaagendamento)}</td>
        <td>${a.valortatuagem ?? '-'}</td>
        <td>${a.status || 'pendente'}</td>
        <td>${imagemHtml}</td>
        <td>
          <button class="btn btn-sm btn-warning me-2" onclick='preencherFormularioEdicao(${JSON.stringify(a)})'>Editar</button>
          <button class="btn btn-sm btn-danger" onclick="deletarAgendamento(${a.idagendamento})">Excluir</button>
        </td>
      </tr>`;
  });
}

function preencherFormularioEdicao(agendamento) {
  document.getElementById('idcliente').value = agendamento.idcliente;
  document.getElementById('idtatuador').value = agendamento.idtatuador;
  document.getElementById('dataagendamento').value =
    String(agendamento.dataagendamento).slice(0, 10);

  document.getElementById('horaagendamento').value =
    formatarHora(agendamento.horaagendamento);

  document.getElementById('descricaotatuagem').value =
    agendamento.descricaotatuagem || '';

  document.getElementById('valortatuagem').value =
    agendamento.valortatuagem ?? '';

  document.getElementById('status').value =
    agendamento.status || 'pendente';

  blocoStatus.style.display = 'block';
  formAgendamento.dataset.idAgendamento = agendamento.idagendamento;

  botaoSubmit.textContent = 'Salvar alteração';
  botaoSubmit.classList.remove('btn-primary');
  botaoSubmit.classList.add('btn-success');

  formAgendamento.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });
}

formAgendamento.addEventListener('submit', async (e) => {
  e.preventDefault();

  const agendamento = {
    idcliente: Number(document.getElementById('idcliente').value),
    idtatuador: Number(document.getElementById('idtatuador').value),
    dataagendamento: document.getElementById('dataagendamento').value,
    horaagendamento: document.getElementById('horaagendamento').value,
    descricaotatuagem: document.getElementById('descricaotatuagem').value || null,
    valortatuagem: document.getElementById('valortatuagem').value
      ? Number(document.getElementById('valortatuagem').value)
      : null,
    status: document.getElementById('status').value
  };

  const idAgendamento = formAgendamento.dataset.idAgendamento;
  let idParaUpload = idAgendamento;

  if (idAgendamento) {
    await fetch(`${API}/agendamentos/${idAgendamento}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(agendamento)
    });
  } else {
    const resposta = await fetch(`${API}/agendamentos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(agendamento)
    });
    const dados = await resposta.json();
    idParaUpload = dados.idagendamento;
  }

  // Certifique-se de que a leitura `.files[0]` está devidamente mapeada aqui
  const arquivo = document.getElementById('desenho').files[0];
  if (arquivo && idParaUpload) {
    const formData = new FormData();
    formData.append('arquivo', arquivo);

    await fetch(`${API}/agendamentos/${idParaUpload}/desenho`, {
      method: 'POST',
      body: formData
    });
  }

  limparFormulario();
  listarAgendamentos();
});
