// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Este é o nosso "banco de dados" na blockchain
contract InsuranceRegistry {

    // Define a estrutura de dados para um seguro
    struct Insurance {
        string id;
        uint256 value; // Usamos uint256 para valores numéricos em Solidity
        string createdAt;
    }

    // Um array público para armazenar todos os seguros
    Insurance[] public insurances;

    // Função para registrar um novo seguro
    // Qualquer um pode chamar esta função para adicionar dados à blockchain
    function registerInsurance(string memory _id, uint256 _value, string memory _createdAt) public {
        // Adiciona um novo seguro ao final do array 'insurances'
        insurances.push(Insurance(_id, _value, _createdAt));
    }

    // Função para obter a quantidade total de seguros registrados
    // Usamos isso para saber quantas vezes precisamos consultar os dados
    function getInsurancesCount() public view returns (uint) {
        return insurances.length;
    }
}