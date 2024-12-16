CREATE TABLE client(
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100)
);

INSERT INTO client(nom, prenom) VALUES('DUPONT', 'Jean');
INSERT INTO client(nom, prenom) VALUES('DURAND', 'Paul');

-- Fonction de remplissage automatique de la table client
CREATE OR REPLACE FUNCTION fill_client_table(num_rows INT)
RETURNS VOID AS $$
DECLARE
i INT;
    noms TEXT[] := ARRAY['Martin', 'Durand', 'Dupont', 'Moreau', 'Lemoine', 'Leroy', 'Garcia', 'Rousseau'];
    prenoms TEXT[] := ARRAY['Jean', 'Paul', 'Marie', 'Sophie', 'Lucas', 'Clara', 'Emma', 'Léa', 'Louis', 'Nathan'];
BEGIN
FOR i IN 1..num_rows LOOP
        INSERT INTO client (nom, prenom)
        VALUES (
            noms[ceil(random() * array_length(noms, 1))],
            prenoms[ceil(random() * array_length(prenoms, 1))]
        );
END LOOP;
END;
$$ LANGUAGE plpgsql;