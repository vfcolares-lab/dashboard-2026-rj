// Carregar secoes_2022_rj.json dinamicamente (arquivo de seções eleitorais RJ)
console.log('📍 Iniciando carregamento de dados de seções eleitorais RJ...');
const startTime = Date.now();

fetch('secoes_2022_rj.json')
    .then(response => {
        console.log(`📊 Response recebido em ${Date.now() - startTime}ms, size: ${response.headers.get('content-length')} bytes`);
        return response.json();
    })
    .then(data => {
        const elapsed = Date.now() - startTime;
        window.SECOES_2022_RJ = data;
        const numSecoes = Object.keys(data).length;
        console.log(`✅ SECOES_2022_RJ carregado em ${elapsed}ms: ${numSecoes} seções eleitorais`);
    })
    .catch(err => {
        console.error(`❌ Erro ao carregar secoes_2022_rj.json após ${Date.now() - startTime}ms:`, err);
        console.error(`   Tipo: ${err.name}, Mensagem: ${err.message}`);
    });
