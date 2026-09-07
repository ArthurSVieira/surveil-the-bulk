from fastapi.testclient import TestClient 
from surveil_the_bulk.app import app

client = TestClient(app)

def test_status_endpoint200():
        response = client.get('/api/status')

        assert response.status_code == 200

        assert response.json() == {"status": "StB API online", "version":"1.0"}

def test_criar_deck_com_dados_faltando_retorna_422():
    payload_incompleto = {
        "name": "Deck Falso",
        "format": "modern"
        # Opa, esquecemos o "color"!
    }
    
    response = client.post("/api/decks", json=payload_incompleto)
    
    assert response.status_code == 422
    
    mensagem_de_erro = response.json()
    print("\nERRO DO FASTAPI:", mensagem_de_erro)