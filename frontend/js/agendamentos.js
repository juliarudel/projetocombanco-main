
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

async function listarAgendamentos() {
  const resposta = await verificarResposta(
    await fetch(`${API}/agendamentos`)
  );

  agendamentosCarregados = await resposta.json();
  corpoTabela.innerHTML = '';

  agendamentosCarregados.forEach(a => {
    const linha = document.createElement('tr');

    const valores = [
      a.idagendamento,
      a.cliente,
      a.tatuador,
      String(a.dataagendamento).slice(0, 10),
      formatarHora(a.horaagendamento),
      a.valortatuagem ?? '-',
      a.status || 'pendente'
    ];

    valores.forEach(valor => {
      const celula = document.createElement('td');
      celula.textContent = valor ?? '';
      linha.appendChild(celula);
    });

    const celulaAcoes = document.createElement('td');

    const botaoEditar = document.createElement('button');
    botaoEditar.type = 'button';
    botaoEditar.className = 'btn btn-sm btn-warning me-2';
    botaoEditar.textContent = 'Editar';
    botaoEditar.addEventListener('click', () => {
      preencherFormularioEdicao(a);
    });

    const botaoExcluir = document.createElement('button');
    botaoExcluir.type = 'button';
    botaoExcluir.className = 'btn btn-sm btn-danger';
    botaoExcluir.textContent = 'Excluir';
    botaoExcluir.addEventListener('click', () => {
      deletarAgendamento(a.idagendamento);
    });

    celulaAcoes.append(botaoEditar, botaoExcluir);
    linha.appendChild(celulaAcoes);
    corpoTabela.appendChild(linha);
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

  const idAgendamento = formAgendamento.dataset.idAgendamento;

  const agendamento = {
    idcliente: Number(document.getElementById('idcliente').value),
    idtatuador: Number(document.getElementById('idtatuador').value),
    dataagendamento: document.getElementById('dataagendamento').value,
    horaagendamento: document.getElementById('horaagendamento').value,
    descricaotatuagem:
      document.getElementById('descricaotatuagem').value || null,
    valortatuagem:
      document.getElementById('valortatuagem').value !== ''
        ? Number(document.getElementById('valortatuagem').value)
        : null
  };

  // Só envia o status quando estiver editando.
  if (idAgendamento !== undefined) {
    agendamento.status = document.getElementById('status').value;
  }

  try {
    botaoSubmit.disabled = true;

    const resposta = await fetch(
      idAgendamento !== undefined
        ? `${API}/agendamentos/${idAgendamento}`
        : `${API}/agendamentos`,
      {
        method: idAgendamento !== undefined ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(agendamento)
      }
    );

    await verificarResposta(resposta);

    alert(
      idAgendamento !== undefined
        ? 'Agendamento atualizado com sucesso!'
        : 'Agendamento cadastrado com sucesso!'
    );

    limparFormulario();
    await listarAgendamentos();

  } catch (erro) {
    console.error('Erro ao salvar agendamento:', erro);
    alert(`Não foi possível salvar: ${erro.message}`);
  } finally {
    botaoSubmit.disabled = false;
  }
});

async function deletarAgendamento(id) {
  if (!confirm('Tem certeza que deseja excluir este agendamento?')) return;

  try {
    const resposta = await fetch(`${API}/agendamentos/${id}`, {
      method: 'DELETE'
    });

    await verificarResposta(resposta);

    alert('Agendamento excluído com sucesso!');
    await listarAgendamentos();

  } catch (erro) {
    console.error('Erro ao excluir:', erro);
    alert(`Não foi possível excluir: ${erro.message}`);
  }
}

// Inicializa a página.
async function inicializar() {
  try {
    await Promise.all([
      carregarClientes(),
      carregarTatuadores()
    ]);

    await listarAgendamentos();
  } catch (erro) {
    console.error('Erro ao carregar a página:', erro);
    alert(`Erro ao carregar dados: ${erro.message}`);
  }
}

inicializar();
