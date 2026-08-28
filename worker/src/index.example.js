async function obterDashboard(env) {
  const raw = await env.OPPORTUNITY_DATA.get("dashboard");

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}


async function enviarTelegram(token, chatId, texto) {
  const resposta = await fetch(
    `https://api.telegram.org/bot${token}/sendMessage`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        chat_id: chatId,
        text: texto,
      }),
    }
  );

  if (!resposta.ok) {
    throw new Error(`Telegram HTTP ${resposta.status}`);
  }
}


export default {
  async fetch(request, env) {
    if (request.method === "GET") {
      return new Response(
        "Michael Opportunity Intelligence — public example",
        {status: 200}
      );
    }

    if (request.method !== "POST") {
      return new Response("Method not allowed", {status: 405});
    }

    const update = await request.json();
    const mensagem = update?.message;

    if (!mensagem) {
      return new Response("OK");
    }

    const texto = (mensagem.text || "").trim().toLowerCase();

    if (texto === "/status") {
      const dashboard = await obterDashboard(env);
      const resposta = dashboard
        ? `Sistema operacional. Vagas atuais: ${dashboard.vagas_atuais || 0}`
        : "Ainda não existe snapshot disponível.";

      await enviarTelegram(
        env.TELEGRAM_BOT_TOKEN,
        mensagem.chat.id,
        resposta
      );
    }

    return new Response("OK");
  },
};
