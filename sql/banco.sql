CREATE DATABASE IF NOT EXISTS ong_adocao_pets CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ong_adocao_pets;

CREATE TABLE IF NOT EXISTS usuarios (
 id INT AUTO_INCREMENT PRIMARY KEY,
 nome VARCHAR(250) NOT NULL,
 email VARCHAR(250) NOT NULL UNIQUE,
 senha_hash VARCHAR(255) NOT NULL,
 perfil VARCHAR(30) NOT NULL,
 telefone VARCHAR(20) NOT NULL,
 cidade VARCHAR(100) NOT NULL,
 criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT chk_perfil CHECK (perfil IN ('adotante','responsavel','administrador'))
);
CREATE TABLE IF NOT EXISTS pets (
 id INT AUTO_INCREMENT PRIMARY KEY,
 responsavel_id INT NOT NULL,
 nome VARCHAR(100) NOT NULL,
 especie VARCHAR(100) NOT NULL,
 raca VARCHAR(100),
 porte VARCHAR(30) NOT NULL,
 sexo VARCHAR(20) NOT NULL,
 idade_meses INT NOT NULL,
 castrado BOOLEAN NOT NULL,
 vacinado BOOLEAN NOT NULL,
 descricao VARCHAR(500) NOT NULL,
 cidade VARCHAR(100) NOT NULL,
 latitude DECIMAL(10,8),
 longitude DECIMAL(11,8),
 status VARCHAR(30) NOT NULL DEFAULT 'Disponivel',
 criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
 CONSTRAINT chk_porte CHECK (porte IN ('Pequeno','Medio','Grande')),
 CONSTRAINT chk_sexo CHECK (sexo IN ('Macho','Femea')),
 CONSTRAINT chk_idade CHECK (idade_meses >= 0),
 CONSTRAINT chk_status_pet CHECK (status IN ('Disponivel','Em processo','Adotado')),
 CONSTRAINT chk_lat CHECK (latitude BETWEEN -90 AND 90),
 CONSTRAINT chk_lng CHECK (longitude BETWEEN -180 AND 180),
 CONSTRAINT chk_coords CHECK ((latitude IS NULL AND longitude IS NULL) OR (latitude IS NOT NULL AND longitude IS NOT NULL)),
 INDEX idx_busca (status, especie, porte, cidade, idade_meses)
);
CREATE TABLE IF NOT EXISTS pedidos_adocao (
 id INT AUTO_INCREMENT PRIMARY KEY,
 pet_id INT NOT NULL,
 adotante_id INT NOT NULL,
 mensagem TEXT NOT NULL,
 status VARCHAR(30) NOT NULL DEFAULT 'Pendente',
 data DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (pet_id) REFERENCES pets(id),
 FOREIGN KEY (adotante_id) REFERENCES usuarios(id),
 CONSTRAINT chk_status_pedido CHECK (status IN ('Pendente','Aceito','Recusado')),
 UNIQUE KEY uq_pedido (pet_id, adotante_id)
);
CREATE TABLE IF NOT EXISTS favoritos (
 usuario_id INT NOT NULL,
 pet_id INT NOT NULL,
 criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY (usuario_id, pet_id),
 FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
 FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS fotos_pets (
 id INT AUTO_INCREMENT PRIMARY KEY,
 pet_id INT NOT NULL,
 caminho_foto VARCHAR(500) NOT NULL,
 principal BOOLEAN NOT NULL DEFAULT FALSE,
 criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS triagem_adotantes (
 id INT AUTO_INCREMENT PRIMARY KEY,
 pedido_id INT NOT NULL UNIQUE,
 tipo_moradia VARCHAR(50) NOT NULL,
 possui_outros_animais BOOLEAN NOT NULL,
 experiencia_com_pets BOOLEAN NOT NULL,
 observacoes TEXT,
 FOREIGN KEY (pedido_id) REFERENCES pedidos_adocao(id) ON DELETE CASCADE,
 CONSTRAINT chk_moradia CHECK (tipo_moradia IN ('Casa','Apartamento','Outro'))
);
