import datetime
from grpc_utils import insurance_service_pb2, insurance_service_pb2_grpc
import json
from web3 import Web3

# ==================== CONFIGURAÇÃO DA BLOCKCHAIN ====================
# Endereço RPC do seu Ganache (verifique no topo da janela do Ganache)
GANACHE_URL = "http://127.0.0.1:7545"

# Cole aqui o endereço do contrato que você copiou do Remix

CONTRACT_ADDRESS = "0xf8e81D47203A594245E36C48e151709F0C19fBe8"

# Cole aqui o ABI que você copiou do Remix.
# É uma lista longa de texto (JSON), pode quebrar em várias linhas.
CONTRACT_ABI = """[
	{
		"inputs": [],
		"name": "getInsurancesCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "insurances",
		"outputs": [
			{
				"internalType": "string",
				"name": "id",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "createdAt",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_id",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_value",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_createdAt",
				"type": "string"
			}
		],
		"name": "registerInsurance",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
"""

# ====================================================================


class InsuranceServiceServicer(insurance_service_pb2_grpc.InsuranceServiceServicer):
    def __init__(self):
        # Conecta ao blockchain
        self.w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
        # Seleciona a primeira conta do Ganache para enviar as transações
        self.account = self.w3.eth.accounts[0]

        # Carrega o contrato inteligente
        self.contract = self.w3.eth.contract(
            address=CONTRACT_ADDRESS,
            abi=json.loads(CONTRACT_ABI) # Carrega o ABI a partir da string JSON
        )
        print("Conectado ao Ethereum e contrato carregado!")
        print("Usando contrato:", CONTRACT_ADDRESS)
        print("Código:", self.w3.eth.get_code(CONTRACT_ADDRESS).hex())

    def RegisterInsurance(self, request, context):
        created_at = datetime.datetime.now().isoformat()

        try:
            # Monta a transação para chamar a função `registerInsurance` do contrato
            tx_hash = self.contract.functions.registerInsurance(
                request.id,
                request.value, # O valor deve ser um número inteiro
                created_at
            ).transact({'from': self.account})

            # Espera a transação ser minerada pela blockchain
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            print(f"[Blockchain] Seguro registrado com sucesso! Transação: {receipt.transactionHash.hex()}")
            return insurance_service_pb2.InsuranceResponse(success=True, id=request.id)

        except Exception as e:
            print(f"Erro ao registrar na blockchain: {e}")
            return insurance_service_pb2.InsuranceResponse(success=False, id=request.id)


    def GetAllInsurances(self, request, context):
        insurances = []
        try:
            # 1. Chama a função `getInsurancesCount` para saber quantos seguros existem
            count = self.contract.functions.getInsurancesCount().call()

            # 2. Itera e busca cada seguro individualmente
            for i in range(count):
                # O array 'insurances' no contrato é público, então podemos chamá-lo como uma função
                # A função 'call()' lê dados sem criar uma transação (não gasta "gás")
                raw_data = self.contract.functions.insurances(i).call()

                # O retorno é uma lista: [id, value, createdAt]
                insurances.append(
                    insurance_service_pb2.InsuranceData(
                        id=raw_data[0],
                        value=raw_data[1],
                        created_at=raw_data[2]
                    )
                )

            print(f"Recuperados {len(insurances)} seguros da blockchain.")
        except Exception as e:
            print(f"Erro ao ler da blockchain: {e}")

        return insurance_service_pb2.InsuranceList(insurances=insurances)