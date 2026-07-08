# EduTech - FrontEnd

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)

## 🎯 Visão Geral

Este repositório contém o código-fonte do **frontend** da **Plataforma Educacional Tech do Instituto Consuelo**. Trata-se de uma plataforma web de educação online com foco em inclusão social e acesso à tecnologia, conectando estudantes, profissionais de tecnologia que produzem conteúdo e administradores em um ambiente simples, acessível e guiado.

O objetivo é reduzir barreiras de entrada no mercado de tecnologia por meio de trilhas de aprendizado pensadas para iniciantes e conteúdos práticos alinhados ao mercado.

---

## ✨ Funcionalidades

O frontend é responsável por toda a interface e experiência do usuário.

- ✅ **Autenticação:** Páginas de Cadastro e Login com validação de formulário.
- ✅ **Páginas Públicas:** Landing Page, Detalhes do Curso.
- ✅ **Design Responsivo:** Interface adaptada para dispositivos móveis e desktop.
- ✅ **Componentização:** UI construída com componentes reutilizáveis e bem definidos.
- 🔄 **Dashboard do Aluno:** Área para visualização de cursos matriculados e progresso. (Em desenvolvimento)
- 🔄 **Dashboard do Professor:** Ferramentas para criação e gerenciamento de cursos. (Em desenvolvimento)
- 🔄 **Painel Administrativo:** Visão geral e gerenciamento da plataforma. (Em desenvolvimento)

---

## 🛠️ Tecnologias Utilizadas

- **[React](https://react.dev/)**: Biblioteca principal para a construção da interface.
- **[TypeScript](https://www.typescriptlang.org/)**: Para tipagem estática e um desenvolvimento mais seguro.
- **[Vite](https://vitejs.dev/)**: Ferramenta de build para um ambiente de desenvolvimento rápido.
- **[Tailwind CSS](https://tailwindcss.com/)**: Framework CSS para estilização rápida e consistente.
- **[React Hook Form](https://react-hook-form.com/)**: Para gerenciamento de formulários.
- **[Zod](https://zod.dev/)**: Para validação de schemas e dados.
- **[tailwind-variants](https://www.tailwind-variants.org/)**: Para criar componentes com variantes de estilo.
- **[Axios](https://axios-http.com/)**: Para realizar requisições HTTP à API do backend.

---

## 🚀 Rodando o Projeto Localmente

Siga os passos abaixo para configurar e executar o projeto em seu ambiente de desenvolvimento.

### Pré-requisitos

- [Node.js](https://nodejs.org/en/) (versão 18 ou superior)
- [Yarn](https://yarnpkg.com/) ou [NPM](https://www.npmjs.com/)

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/Edutech-Instituto-Consuelo/frontend.git
   ```

2. **Navegue até o diretório do projeto:**
   ```bash
   cd frontend
   ```

3. **Instale as dependências:**
   ```bash
   npm install
   ```
   _ou_
   ```bash
   yarn install
   ```

4. **Configure as variáveis de ambiente:**
   
   Crie um arquivo `.env` na raiz do projeto para definir a URL da API.

   **Opção 1: Rodando com Backend Local (Recomendado)**
   
   No arquivo `.env`:
   ```env
   VITE_API_URL=/api
   ```

   ⚠️ **Importante:** Para essa opção funcionar, adicione a configuração de proxy no seu `vite.config.ts`:

   ```typescript
   // vite.config.ts
   export default defineConfig({
     // ...
    server: {
      proxy: {
        '/api': {
           target: 'http://localhost:8000',
           changeOrigin: true,
           rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
   });
   ```

   **Opção 2: Rodando com API de Produção**
   
   Caso queira conectar diretamente a API em produção:
   ```env
   VITE_API_URL=https://backend-6ga7.onrender.com/
   ```
   


5. **Execute o projeto:**
   ```bash
   npm run **dev**
   ```
   A aplicação estará disponível em `http://localhost:5173` (ou outra porta indicada no terminal).

---

## Links

- [**GitHub Projects**](https://github.com/orgs/Edutech-Instituto-Consuelo/projects/4)
- [**Site**](https://plataforma-instituto-consuelo.vercel.app/)
- [**BackEnd**](https://github.com/Edutech-Instituto-Consuelo/backend)

