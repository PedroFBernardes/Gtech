const botaoChat = document.getElementById('botaoChat');
const janelaChat = document.getElementById('janelaChat');
const fecharChat = document.getElementById('fecharChat');
const formChat = document.getElementById('formChat');
const entradaMensagem = document.getElementById('entradaMensagem');
const listaMensagens = document.getElementById('listaMensagens');

function abrirJanela() {
  janelaChat.classList.add('aberta');
  janelaChat.setAttribute('aria-hidden', 'false');
  setTimeout(() => entradaMensagem?.focus(), 50);
}

function fecharJanela() {
  janelaChat.classList.remove('aberta');
  janelaChat.setAttribute('aria-hidden', 'true');
}

function rolarAteFinal() {
  listaMensagens.scrollTop = listaMensagens.scrollHeight;
}

function criarBolhaUsuario(texto) {
  const html = `
    <div class="mensagem mensagem--usuario">
      <span class="mensagem__autor">Você</span>
      <p class="mensagem__texto"></p>
      <time class="mensagem__tempo">${new Date().toLocaleTimeString().slice(0,5)}</time>
    </div>`;
  listaMensagens.insertAdjacentHTML('beforeend', html);
  listaMensagens.lastElementChild.querySelector('.mensagem__texto').textContent = texto;
  rolarAteFinal();
}

function criarBolhaBot(textoInicial = 'Analisando ...') {
  const html = `
    <div class="mensagem mensagem--bot">
      <span class="mensagem__autor">GTECH</span>
      <p class="mensagem__texto">${textoInicial}</p>
      <time class="mensagem__tempo">${new Date().toLocaleTimeString().slice(0,5)}</time>
    </div>`;
  listaMensagens.insertAdjacentHTML('beforeend', html);
  rolarAteFinal();
  return listaMensagens.lastElementChild; // retorna o nó para atualizar depois
}

// --------- Eventos UI ---------
botaoChat?.addEventListener('click', abrirJanela);
fecharChat?.addEventListener('click', fecharJanela);

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && janelaChat.classList.contains('aberta')) fecharJanela();
});

// --------- Enviar mensagem para o back-end ---------
formChat?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const texto = entradaMensagem.value.trim();
  if (!texto) return;

  criarBolhaUsuario(texto);
  entradaMensagem.value = '';

  const bolhaBot = criarBolhaBot('Analisando ...');

  try {
    // use caminho relativo para evitar CORS: mesma origem do Flask
    const resposta = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ msg: texto })
    });

    if (!resposta.ok) {
      const detalhe = await resposta.text();
      bolhaBot.querySelector('.mensagem__texto').textContent =
        `Erro ${resposta.status}: ${detalhe || 'Falha ao consultar o assistente.'}`;
      return;
    }

    // Back-end retorna texto puro
    const textoDaResposta = await resposta.text();
    bolhaBot.querySelector('.mensagem__texto').innerHTML =
      textoDaResposta.replace(/\n/g, '<br>');
    rolarAteFinal();
  } catch (erro) {
    bolhaBot.querySelector('.mensagem__texto').textContent =
      `Erro de rede: ${erro?.message || erro}`;
  }
});
