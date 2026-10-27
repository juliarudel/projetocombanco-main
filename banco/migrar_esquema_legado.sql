-- Migration from the earlier plural-table schema to the application schema.
-- Preserves existing rows; do not run more than once.

USE estudio_tatuagem;

ALTER TABLE agendamento
  DROP FOREIGN KEY agendamento_ibfk_2,
  DROP INDEX idtatuadores,
  CHANGE COLUMN idtatuadores idtatuador INT(11) NOT NULL;

ALTER TABLE tatuadores
  DROP FOREIGN KEY tatuadores_ibfk_1;

RENAME TABLE tatuadores TO tatuador;

ALTER TABLE tatuador
  CHANGE COLUMN idtatuadores idtatuador INT(11) NOT NULL AUTO_INCREMENT,
  CHANGE COLUMN nome nometatuador VARCHAR(150) NOT NULL,
  MODIFY COLUMN email VARCHAR(150) DEFAULT NULL,
  MODIFY COLUMN idsenioridade INT(11) NOT NULL,
  ADD COLUMN cpf CHAR(11) NOT NULL AFTER nometatuador,
  ADD COLUMN telefone VARCHAR(20) DEFAULT NULL AFTER email,
  ADD COLUMN datacontratacao DATE DEFAULT NULL AFTER telefone,
  ADD UNIQUE KEY cpf (cpf),
  ADD CONSTRAINT tatuador_ibfk_1
    FOREIGN KEY (idsenioridade) REFERENCES senioridade (idsenioridade);

ALTER TABLE cliente
  MODIFY COLUMN email VARCHAR(150) DEFAULT NULL,
  ADD COLUMN cpf CHAR(11) NOT NULL AFTER nome,
  ADD COLUMN datacadastro DATE DEFAULT NULL AFTER telefone,
  ADD COLUMN cidade VARCHAR(100) DEFAULT NULL AFTER datacadastro,
  ADD COLUMN uf CHAR(2) DEFAULT NULL AFTER cidade,
  ADD UNIQUE KEY cpf (cpf);

RENAME TABLE estilos TO estilo;

ALTER TABLE estilo
  CHANGE COLUMN idestilos idestilo INT(11) NOT NULL AUTO_INCREMENT,
  CHANGE COLUMN nome descricao VARCHAR(100) NOT NULL;

CREATE TABLE tatuador_estilo (
  idtatuador INT(11) NOT NULL,
  idestilo INT(11) NOT NULL,
  dataestilo DATE DEFAULT NULL,
  PRIMARY KEY (idtatuador, idestilo),
  KEY idestilo (idestilo),
  CONSTRAINT tatuador_estilo_ibfk_1
    FOREIGN KEY (idtatuador) REFERENCES tatuador (idtatuador),
  CONSTRAINT tatuador_estilo_ibfk_2
    FOREIGN KEY (idestilo) REFERENCES estilo (idestilo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE agendamento
  ADD COLUMN dataagendamento DATE DEFAULT NULL AFTER idtatuador,
  ADD COLUMN horaagendamento TIME DEFAULT NULL AFTER dataagendamento,
  ADD COLUMN descricaotatuagem TEXT DEFAULT NULL AFTER horaagendamento,
  ADD COLUMN desenhoaprovado VARCHAR(255) DEFAULT NULL AFTER descricaotatuagem,
  ADD COLUMN valortatuagem DECIMAL(10,2) DEFAULT NULL AFTER desenhoaprovado,
  ADD COLUMN status ENUM('pendente','confirmado','concluido','cancelado')
    NOT NULL DEFAULT 'pendente' AFTER valortatuagem;

UPDATE agendamento
SET dataagendamento = DATE(data_hora),
    horaagendamento = TIME(data_hora);

ALTER TABLE agendamento
  MODIFY COLUMN dataagendamento DATE NOT NULL,
  MODIFY COLUMN horaagendamento TIME NOT NULL,
  ADD KEY idtatuador (idtatuador),
  ADD CONSTRAINT agendamento_ibfk_2
    FOREIGN KEY (idtatuador) REFERENCES tatuador (idtatuador);
