export function maskDateTime(dateTime: Date|string|number): string {
    // Espera uma string no formato "YYYY-MM-DDTHH:MM:SSZ"
    const date = new Date(dateTime);
    return date.toLocaleString('pt-BR');
}