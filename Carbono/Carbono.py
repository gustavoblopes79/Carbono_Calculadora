import customtkinter as ctk
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Union
import json

# Para gráficos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# --- CLASSE CALCULADORA CARBONO (ADAPTAÇÕES PARA SALVAR/CARREGAR/GRÁFICOS) ---
class CalculadoraCarbono:
    def __init__(self, nome_empresa: str):
        self.nome_empresa = nome_empresa.strip()
        self.registros_emissoes = []
        self.registros_remocoes = []
        self.creditos_assinatura_disponiveis = 0.0

    def adicionar_emissao(self, fonte: str, quantidade_co2e_toneladas: float):
        if not isinstance(fonte, str) or not fonte.strip():
            raise ValueError("Erro: A fonte da emissão não pode ser vazia ou inválida.")
        if not isinstance(quantidade_co2e_toneladas, (int, float)) or quantidade_co2e_toneladas < 0:
            raise ValueError("Erro: A quantidade de CO2e para emissão deve ser um número positivo.")
        self.registros_emissoes.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fonte": fonte.strip(),
            "quantidade_co2e_toneladas": float(quantidade_co2e_toneladas)
        })

    def adicionar_remocao(self, tipo: str, quantidade_co2e_toneladas: float):
        if not isinstance(tipo, str) or not tipo.strip():
            raise ValueError("Erro: O tipo de remoção não pode ser vazio ou inválido.")
        if not isinstance(quantidade_co2e_toneladas, (int, float)) or quantidade_co2e_toneladas < 0:
            raise ValueError("Erro: A quantidade de CO2e para remoção deve ser um número positivo.")
        self.registros_remocoes.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo.strip(),
            "quantidade_co2e_toneladas": float(quantidade_co2e_toneladas)
        })

    def adicionar_creditos_assinatura(self, quantidade_creditos: float):
        if not isinstance(quantidade_creditos, (int, float)) or quantidade_creditos < 0:
            raise ValueError("Erro: A quantidade de créditos de assinatura deve ser um número positivo.")
        self.creditos_assinatura_disponiveis += float(quantidade_creditos)

    def calcular_total_emissoes(self) -> float:
        return sum(e["quantidade_co2e_toneladas"] for e in self.registros_emissoes)

    def calcular_total_remocoes(self) -> float:
        return sum(r["quantidade_co2e_toneladas"] for r in self.registros_remocoes)

    def calcular_balanco_carbono(self) -> tuple[float, float, float]:
        total_emissoes = self.calcular_total_emissoes()
        total_remocoes = self.calcular_total_remocoes()
        balanco = total_emissoes - total_remocoes
        return balanco, total_emissoes, total_remocoes

    def calcular_creditos_necessarios_ou_excedente(self) -> tuple[float, float]:
        balanco_carbono_liquido, _, _ = self.calcular_balanco_carbono()
        creditos_necessarios = 0.0
        creditos_excedentes = 0.0
        if balanco_carbono_liquido > 0:
            if self.creditos_assinatura_disponiveis >= balanco_carbono_liquido:
                creditos_excedentes = self.creditos_assinatura_disponiveis - balanco_carbono_liquido
            else:
                creditos_necessarios = balanco_carbono_liquido - self.creditos_assinatura_disponiveis
        else:
            creditos_excedentes = abs(balanco_carbono_liquido) + self.creditos_assinatura_disponiveis
        return creditos_necessarios, creditos_excedentes

    def gerar_relatorio_str(self) -> str:
        # Conteúdo do relatório (inalterado)
        relatorio = []
        relatorio.append("="*60)
        relatorio.append(f"   RELATÓRIO DE BALANÇO E CRÉDITO DE CARBONO - {self.nome_empresa.upper()}   ")
        relatorio.append("="*60)
        relatorio.append(f"Data do Relatório: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        total_emissoes = self.calcular_total_emissoes()
        total_remocoes = self.calcular_total_remocoes()
        balanco_carbono, _, _ = self.calcular_balanco_carbono()
        creditos_necessarios, creditos_excedentes = self.calcular_creditos_necessarios_ou_excedente()
        relatorio.append("\n--- Balanço Geral de Carbono ---")
        relatorio.append(f"  Total de Emissões Registradas: {total_emissoes:.2f} toneladas de CO2e")
        relatorio.append(f"  Total de Remoções Registradas: {total_remocoes:.2f} toneladas de CO2e")
        relatorio.append(f"  Créditos de Assinatura Disponíveis: {self.creditos_assinatura_disponiveis:.2f} créditos (toneladas de CO2e)")
        relatorio.append(f"\n  Balanço Líquido de Carbono (Emissões - Remoções): {balanco_carbono:.2f} toneladas de CO2e")
        if balanco_carbono > 0:
            relatorio.append("  Status do Balanço: Superávit de Emissões (Emite mais do que remove)")
        elif balanco_carbono < 0:
            relatorio.append("  Status do Balanço: Déficit de Emissões / Sequestro Líquido (Remove mais do que emite)")
        else:
            relatorio.append("  Status do Balanço: Neutro (Emissões = Remoções)")
        relatorio.append("\n--- Análise de Créditos de Carbono ---")
        if creditos_necessarios > 0:
            relatorio.append(f"  Necessidade de Créditos de Carbono: {creditos_necessarios:.2f} toneladas de CO2e")
            relatorio.append("  Atenção: Você precisa adquirir mais créditos para atingir a neutralidade.")
        elif creditos_excedentes > 0:
            relatorio.append(f"  Excedente de Créditos de Carbono: {creditos_excedentes:.2f} toneladas de CO2e")
            relatorio.append("  Parabéns! Você tem créditos excedentes que podem ser transacionados ou usados no futuro.")
        else:
            relatorio.append("  Status: Neutralidade de Carbono alcançada ou não há créditos/necessidade no momento.")
        relatorio.append("\n--- Detalhes dos Registros de Emissões ---")
        if self.registros_emissoes:
            for i, reg in enumerate(self.registros_emissoes):
                relatorio.append(f"  {i+1}. Data: {reg['data']}, Fonte: '{reg['fonte']}', Quantidade: {reg['quantidade_co2e_toneladas']:.2f} CO2e")
        else:
            relatorio.append("  Nenhum registro de emissão.")
        relatorio.append("\n--- Detalhes dos Registros de Remoções ---")
        if self.registros_remocoes:
            for i, reg in enumerate(self.registros_remocoes):
                relatorio.append(f"  {i+1}. Data: {reg['data']}, Tipo: '{reg['tipo']}', Quantidade: {reg['quantidade_co2e_toneladas']:.2f} CO2e")
        else:
            relatorio.append("  Nenhum registro de remoção.")
        relatorio.append("\n" + "="*60)
        return "\n".join(relatorio)

    def to_dict(self) -> dict:
        """Converte o objeto CalculadoraCarbono em um dicionário para serialização JSON."""
        return {
            "nome_empresa": self.nome_empresa,
            "registros_emissoes": self.registros_emissoes,
            "registros_remocoes": self.registros_remocoes,
            "creditos_assinatura_disponiveis": self.creditos_assinatura_disponiveis
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Cria uma instância de CalculadoraCarbono a partir de um dicionário (JSON)."""
        calculadora = cls(data["nome_empresa"])
        calculadora.registros_emissoes = data.get("registros_emissoes", [])
        calculadora.registros_remocoes = data.get("registros_remocoes", [])
        calculadora.creditos_assinatura_disponiveis = data.get("creditos_assinatura_disponiveis", 0.0)
        return calculadora

# --- CLASSE APP (COM BOTÕES DE SALVAR/CARREGAR E GRÁFICOS) ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora de Crédito de Carbono")
        self.geometry("800x680") # Ajustado o tamanho da janela principal para caber mais
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.calculadora = None
        self.toplevel_report_window = None # Renomeado para maior clareza
        self.toplevel_graph_window = None # Para controlar a janela do gráfico

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Título da Aplicação
        self.title_label = ctk.CTkLabel(self.main_frame, text="Calculadora de Carbono", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=(20, 10))

        # Nome da Empresa
        self.company_name_label = ctk.CTkLabel(self.main_frame, text="Nome da Empresa:")
        self.company_name_label.grid(row=1, column=0, sticky="w", padx=20)
        self.company_name_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Digite o nome da empresa")
        self.company_name_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

        # Botão para iniciar ou resetar a empresa
        self.start_company_button = ctk.CTkButton(self.main_frame, text="Iniciar Nova Empresa", command=self.start_company_calculation)
        self.start_company_button.grid(row=3, column=0, pady=(10, 10), padx=20)

        # Botões de Salvar e Carregar
        self.save_load_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.save_load_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=5)
        self.save_load_frame.grid_columnconfigure(0, weight=1)
        self.save_load_frame.grid_columnconfigure(1, weight=1)

        self.save_button = ctk.CTkButton(self.save_load_frame, text="Salvar Dados", command=self.save_data)
        self.save_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.load_button = ctk.CTkButton(self.save_load_frame, text="Carregar Dados", command=self.load_data)
        self.load_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Labels e Entradas para Emissões
        self.emission_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.emission_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        self.emission_frame.grid_columnconfigure(0, weight=1)
        self.emission_frame.grid_columnconfigure(1, weight=1)

        self.emission_label = ctk.CTkLabel(self.emission_frame, text="Emissões:", font=ctk.CTkFont(weight="bold"))
        self.emission_label.grid(row=0, column=0, columnspan=2, pady=5)

        self.emission_source_label = ctk.CTkLabel(self.emission_frame, text="Fonte:")
        self.emission_source_label.grid(row=1, column=0, sticky="w", padx=(10,0))
        self.emission_source_entry = ctk.CTkEntry(self.emission_frame, placeholder_text="Ex: Energia, Frotas")
        self.emission_source_entry.grid(row=1, column=1, sticky="ew", padx=(0,10))

        self.emission_amount_label = ctk.CTkLabel(self.emission_frame, text="Quantidade (ton CO2e):")
        self.emission_amount_label.grid(row=2, column=0, sticky="w", padx=(10,0))
        self.emission_amount_entry = ctk.CTkEntry(self.emission_frame, placeholder_text="0.0")
        self.emission_amount_entry.grid(row=2, column=1, sticky="ew", padx=(0,10))

        self.add_emission_button = ctk.CTkButton(self.emission_frame, text="Adicionar Emissão", command=self.add_emission)
        self.add_emission_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Labels e Entradas para Remoções
        self.removal_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.removal_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        self.removal_frame.grid_columnconfigure(0, weight=1)
        self.removal_frame.grid_columnconfigure(1, weight=1)

        self.removal_label = ctk.CTkLabel(self.removal_frame, text="Remoções:", font=ctk.CTkFont(weight="bold"))
        self.removal_label.grid(row=0, column=0, columnspan=2, pady=5)

        self.removal_type_label = ctk.CTkLabel(self.removal_frame, text="Tipo:")
        self.removal_type_label.grid(row=1, column=0, sticky="w", padx=(10,0))
        self.removal_type_entry = ctk.CTkEntry(self.removal_frame, placeholder_text="Ex: Reflorestamento, Solar")
        self.removal_type_entry.grid(row=1, column=1, sticky="ew", padx=(0,10))

        self.removal_amount_label = ctk.CTkLabel(self.removal_frame, text="Quantidade (ton CO2e):")
        self.removal_amount_label.grid(row=2, column=0, sticky="w", padx=(10,0))
        self.removal_amount_entry = ctk.CTkEntry(self.removal_frame, placeholder_text="0.0")
        self.removal_amount_entry.grid(row=2, column=1, sticky="ew", padx=(0,10))

        self.add_removal_button = ctk.CTkButton(self.removal_frame, text="Adicionar Remoção", command=self.add_removal)
        self.add_removal_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Labels e Entradas para Créditos de Assinatura
        self.credits_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.credits_frame.grid(row=7, column=0, sticky="ew", padx=20, pady=10)
        self.credits_frame.grid_columnconfigure(0, weight=1)
        self.credits_frame.grid_columnconfigure(1, weight=1)

        self.credits_label = ctk.CTkLabel(self.credits_frame, text="Créditos de Assinatura:", font=ctk.CTkFont(weight="bold"))
        self.credits_label.grid(row=0, column=0, columnspan=2, pady=5)

        self.credits_amount_label = ctk.CTkLabel(self.credits_frame, text="Quantidade (créditos):")
        self.credits_amount_label.grid(row=1, column=0, sticky="w", padx=(10,0))
        self.credits_amount_entry = ctk.CTkEntry(self.credits_frame, placeholder_text="0.0")
        self.credits_amount_entry.grid(row=1, column=1, sticky="ew", padx=(0,10))

        self.add_credits_button = ctk.CTkButton(self.credits_frame, text="Adicionar Créditos", command=self.add_credits)
        self.add_credits_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Botões para Relatório e Gráfico
        self.report_graph_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.report_graph_frame.grid(row=8, column=0, sticky="ew", padx=20, pady=(10, 20))
        self.report_graph_frame.grid_columnconfigure(0, weight=1)
        self.report_graph_frame.grid_columnconfigure(1, weight=1)

        self.generate_report_button = ctk.CTkButton(self.report_graph_frame, text="Ver Relatório de Carbono", command=self.open_report_window)
        self.generate_report_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.generate_graph_button = ctk.CTkButton(self.report_graph_frame, text="Ver Gráfico de Balanço", command=self.open_graph_window)
        self.generate_graph_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Configurar estado inicial dos controles
        self.set_controls_state("disabled")

    def set_controls_state(self, state: str):
        """Habilita ou desabilita os controles de entrada de dados."""
        widgets = [
            self.emission_source_entry, self.emission_amount_entry, self.add_emission_button,
            self.removal_type_entry, self.removal_amount_entry, self.add_removal_button,
            self.credits_amount_entry, self.add_credits_button,
            self.save_button, self.load_button,
            self.generate_report_button, self.generate_graph_button # Incluir botão do gráfico
        ]
        for widget in widgets:
            widget.configure(state=state)

    def start_company_calculation(self):
        """Inicia uma nova calculadora para a empresa informada."""
        company_name = self.company_name_entry.get().strip()
        if not company_name:
            messagebox.showwarning("Aviso", "Por favor, digite o nome da empresa para iniciar.")
            return

        self.calculadora = CalculadoraCarbono(company_name)
        messagebox.showinfo("Sucesso", f"Cálculo iniciado para a empresa: {company_name}")
        self.set_controls_state("normal")
        # Limpar campos de entrada para nova empresa (opcional)
        self.emission_source_entry.delete(0, tk.END)
        self.emission_amount_entry.delete(0, tk.END)
        self.removal_type_entry.delete(0, tk.END)
        self.removal_amount_entry.delete(0, tk.END)
        self.credits_amount_entry.delete(0, tk.END)
        
        # Fechar janelas de relatório/gráfico se abertas
        if self.toplevel_report_window and self.toplevel_report_window.winfo_exists():
            self.toplevel_report_window.destroy()
        if self.toplevel_graph_window and self.toplevel_graph_window.winfo_exists():
            self.toplevel_graph_window.destroy()


    def save_data(self):
        """Salva os dados da calculadora atual em um arquivo JSON."""
        if not self.calculadora:
            messagebox.showwarning("Aviso", "Nenhum dado para salvar. Inicie uma empresa primeiro.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"{self.calculadora.nome_empresa.replace(' ', '_').replace('.', '')}_dados.json"
        )
        if file_path:
            try:
                data_to_save = self.calculadora.to_dict()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, indent=4)
                messagebox.showinfo("Sucesso", f"Dados de '{self.calculadora.nome_empresa}' salvos com sucesso em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar os dados:\n{e}")

    def load_data(self):
        """Carrega dados de um arquivo JSON para a calculadora."""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # Criar nova instância da calculadora a partir dos dados carregados
                self.calculadora = CalculadoraCarbono.from_dict(loaded_data)
                self.company_name_entry.delete(0, tk.END)
                self.company_name_entry.insert(0, self.calculadora.nome_empresa)
                
                messagebox.showinfo("Sucesso", f"Dados de '{self.calculadora.nome_empresa}' carregados com sucesso!")
                self.set_controls_state("normal")
                # Limpar campos de entrada, pois os dados estão carregados internamente
                self.emission_source_entry.delete(0, tk.END)
                self.emission_amount_entry.delete(0, tk.END)
                self.removal_type_entry.delete(0, tk.END)
                self.removal_amount_entry.delete(0, tk.END)
                self.credits_amount_entry.delete(0, tk.END)

                # Fechar janelas de relatório/gráfico se abertas
                if self.toplevel_report_window and self.toplevel_report_window.winfo_exists():
                    self.toplevel_report_window.destroy()
                if self.toplevel_graph_window and self.toplevel_graph_window.winfo_exists():
                    self.toplevel_graph_window.destroy()

            except FileNotFoundError:
                messagebox.showerror("Erro ao Carregar", "Arquivo não encontrado.")
            except json.JSONDecodeError:
                messagebox.showerror("Erro ao Carregar", "Arquivo JSON inválido ou corrompido.")
            except Exception as e:
                messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar os dados:\n{e}")

    def _get_numeric_input(self, entry_widget: ctk.CTkEntry, field_name: str) -> Union[float, None]:
        # ... (método inalterado, já corrigido com Union) ...
        value_str = entry_widget.get().replace(',', '.')
        if not value_str:
            messagebox.showwarning("Entrada Inválida", f"Por favor, digite a quantidade para {field_name}.")
            return None
        try:
            value = float(value_str)
            if value < 0:
                messagebox.showwarning("Entrada Inválida", f"A quantidade para {field_name} deve ser um número positivo.")
                return None
            return value
        except ValueError:
            messagebox.showwarning("Entrada Inválida", f"'{value_str}' não é um número válido para {field_name}. Por favor, digite apenas números.")
            return None

    def add_emission(self):
        # ... (método inalterado) ...
        if not self.calculadora:
            messagebox.showwarning("Aviso", "Inicie uma empresa primeiro!")
            return

        source = self.emission_source_entry.get().strip()
        amount = self._get_numeric_input(self.emission_amount_entry, "Emissão")

        if source and amount is not None:
            try:
                self.calculadora.adicionar_emissao(source, amount)
                messagebox.showinfo("Sucesso", f"Emissão de {amount:.2f} CO2e de '{source}' adicionada.")
                self.emission_source_entry.delete(0, tk.END)
                self.emission_amount_entry.delete(0, tk.END)
            except ValueError as e:
                messagebox.showerror("Erro ao Adicionar", str(e))
        elif not source:
            messagebox.showwarning("Aviso", "Por favor, digite a fonte da emissão.")

    def add_removal(self):
        # ... (método inalterado) ...
        if not self.calculadora:
            messagebox.showwarning("Aviso", "Inicie uma empresa primeiro!")
            return

        type_removal = self.removal_type_entry.get().strip()
        amount = self._get_numeric_input(self.removal_amount_entry, "Remoção")

        if type_removal and amount is not None:
            try:
                self.calculadora.adicionar_remocao(type_removal, amount)
                messagebox.showinfo("Sucesso", f"Remoção de {amount:.2f} CO2e por '{type_removal}' adicionada.")
                self.removal_type_entry.delete(0, tk.END)
                self.removal_amount_entry.delete(0, tk.END)
            except ValueError as e:
                messagebox.showerror("Erro ao Adicionar", str(e))
        elif not type_removal:
            messagebox.showwarning("Aviso", "Por favor, digite o tipo de remoção.")

    def add_credits(self):
        # ... (método inalterado) ...
        if not self.calculadora:
            messagebox.showwarning("Aviso", "Inicie uma empresa primeiro!")
            return

        amount = self._get_numeric_input(self.credits_amount_entry, "Créditos")

        if amount is not None:
            try:
                self.calculadora.adicionar_creditos_assinatura(amount)
                messagebox.showinfo("Sucesso", f"{amount:.2f} créditos de assinatura adicionados.")
                self.credits_amount_entry.delete(0, tk.END)
            except ValueError as e:
                messagebox.showerror("Erro ao Adicionar", str(e))

    def open_report_window(self):
        # ... (método inalterado) ...
        if not self.calculadora:
            messagebox.showwarning("Aviso", "Inicie uma empresa e adicione alguns dados primeiro para gerar o relatório.")
            return
        
        if self.toplevel_report_window is None or not self.toplevel_report_window.winfo_exists():
            self.toplevel_report_window = ReportWindow(self.calculadora, self)
        else:
            self.toplevel_report_window.focus()

    def open_graph_window(self):
        """Abre uma nova janela para exibir um gráfico de balanço de carbono."""
        if not self.calculadora:
            messagebox.showwarning("Aviso", "Inicie uma empresa e adicione dados de emissão/remoção para gerar o gráfico.")
            return

        if self.calculadora.calcular_total_emissoes() == 0 and self.calculadora.calcular_total_remocoes() == 0:
            messagebox.showwarning("Aviso", "Não há dados de emissão ou remoção para gerar o gráfico.")
            return

        if self.toplevel_graph_window is None or not self.toplevel_graph_window.winfo_exists():
            self.toplevel_graph_window = GraphWindow(self.calculadora, self)
        else:
            self.toplevel_graph_window.focus()


# --- CLASSE PARA A JANELA DO RELATÓRIO (INALTERADA) ---
class ReportWindow(ctk.CTkToplevel):
    def __init__(self, calculadora: CalculadoraCarbono, master_app):
        super().__init__(master=master_app)
        self.calculadora = calculadora
        self.master_app = master_app

        self.title(f"Relatório de Carbono - {self.calculadora.nome_empresa}")
        self.geometry("700x750")
        self.transient(master_app)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.report_frame = ctk.CTkFrame(self, corner_radius=10)
        self.report_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.report_frame.grid_columnconfigure(0, weight=1)
        self.report_frame.grid_rowconfigure(0, weight=1)

        self.report_textbox = ctk.CTkTextbox(self.report_frame, wrap="word")
        self.report_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.report_textbox.configure(state="disabled")

        self._load_report()

        self.close_button = ctk.CTkButton(self.report_frame, text="Fechar Relatório", command=self.destroy)
        self.close_button.grid(row=1, column=0, pady=(10, 0))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _load_report(self):
        report_text = self.calculadora.gerar_relatorio_str()
        self.report_textbox.configure(state="normal")
        self.report_textbox.delete("1.0", tk.END)
        self.report_textbox.insert("1.0", report_text)
        self.report_textbox.configure(state="disabled")

    def on_closing(self):
        self.master_app.grab_release()
        self.destroy()

# --- NOVA CLASSE PARA A JANELA DO GRÁFICO ---
class GraphWindow(ctk.CTkToplevel):
    def __init__(self, calculadora: CalculadoraCarbono, master_app):
        super().__init__(master=master_app)
        self.calculadora = calculadora
        self.master_app = master_app

        self.title(f"Gráfico de Balanço de Carbono - {self.calculadora.nome_empresa}")
        self.geometry("700x600")
        self.transient(master_app)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.graph_frame = ctk.CTkFrame(self, corner_radius=10)
        self.graph_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.graph_frame.grid_columnconfigure(0, weight=1)
        self.graph_frame.grid_rowconfigure(0, weight=1)
        
        self._create_graph()

        self.close_button = ctk.CTkButton(self.graph_frame, text="Fechar Gráfico", command=self.destroy)
        self.close_button.grid(row=1, column=0, pady=(10, 0))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_graph(self):
        """Cria o gráfico de barras de emissões e remoções."""
        total_emissoes = self.calculadora.calcular_total_emissoes()
        total_remocoes = self.calculadora.calcular_total_remocoes()
        balanco_liquido, _, _ = self.calculadora.calcular_balanco_carbono()
        
        # Dados para o gráfico
        labels = ['Emissões Totais', 'Remoções Totais', 'Balanço Líquido']
        values = [total_emissoes, total_remocoes, balanco_liquido]
        
        # Cores
        colors = ['red', 'green', 'blue' if balanco_liquido <= 0 else 'orange'] # Azul para neutro/positivo, Laranja para Superavit

        # Criar a figura do Matplotlib
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        
        # Criar o gráfico de barras
        ax.bar(labels, values, color=colors)
        ax.set_ylabel('CO2e (toneladas)')
        ax.set_title(f'Balanço de Carbono para {self.calculadora.nome_empresa}')
        ax.axhline(0, color='gray', linewidth=0.8) # Linha de neutralidade no zero

        # Ajustes para melhor visualização (opcional)
        fig.tight_layout()
        
        # Incorporar o gráfico no CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Adicionar barra de ferramentas (zoom, pan, etc.)
        toolbar_frame = ctk.CTkFrame(self.graph_frame)
        toolbar_frame.grid(row=2, column=0, pady=(5,0), sticky="ew") # Nova linha para a barra de ferramentas
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas_widget.focus_set() # Foca no canvas para interações

    def on_closing(self):
        self.master_app.grab_release()
        plt.close(self.master_app.toplevel_graph_window._get_figure()) # Fecha a figura do matplotlib
        self.destroy()

# --- Configurações e Inicialização da Aplicação Principal ---
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = App()
    app.mainloop()