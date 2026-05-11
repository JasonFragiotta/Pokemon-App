from pathlib import Path
import csv

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, create_engine, select

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pokemon.db"
CSV_PATH = BASE_DIR / "Pokemon.csv"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, connect_args={"check_same_thread": False})

class Pokemon(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dex_number: int = Field(index=True)
    name: str
    type1: str | None = None
    type2: str | None = None
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int
    generation: int
    legendary: bool


class PokemonUpdate(SQLModel):
    name: str | None = None
    type1: str | None = None
    type2: str | None = None
    hp: int | None = None
    attack: int | None = None
    defense: int | None = None
    sp_atk: int | None = None
    sp_def: int | None = None
    speed: int | None = None
    generation: int | None = None
    legendary: bool | None = None


class PokemonCreate(SQLModel):
    dex_number: int
    name: str
    type1: str | None = None
    type2: str | None = None
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int
    generation: int
    legendary: bool


app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def load_csv_into_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(Pokemon)).first()
        if existing is not None:
            return

        if not CSV_PATH.exists():
            raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")

        with CSV_PATH.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            pokemons = []
            for row in reader:
                pokemons.append(
                    Pokemon(
                        dex_number=int(row["#"]),
                        name=row["Name"].strip(),
                        type1=row["Type 1"].strip() or None,
                        type2=row["Type 2"].strip() or None,
                        total=int(row["Total"]),
                        hp=int(row["HP"]),
                        attack=int(row["Attack"]),
                        defense=int(row["Defense"]),
                        sp_atk=int(row["Sp. Atk"]),
                        sp_def=int(row["Sp. Def"]),
                        speed=int(row["Speed"]),
                        generation=int(row["Generation"]),
                        legendary=row["Legendary"].strip().lower() == "true",
                    )
                )
            session.add_all(pokemons)
            session.commit()


@app.on_event("startup")
def startup_event():
    load_csv_into_db()


@app.get("/", response_class=HTMLResponse)
def root():
    html_path = BASE_DIR / "static" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/pokemon")
def list_pokemon():
    with Session(engine) as session:
        results = session.exec(select(Pokemon).order_by(Pokemon.id)).all()
        return results


@app.get("/api/pokemon/{pokemon_id}")
def get_pokemon(pokemon_id: int):
    with Session(engine) as session:
        pokemon = session.exec(select(Pokemon).where(Pokemon.id == pokemon_id)).one_or_none()
        if not pokemon:
            raise HTTPException(status_code=404, detail="Pokemon not found")
        return pokemon


@app.patch("/api/pokemon/{pokemon_id}")
def update_pokemon(pokemon_id: int, updated: PokemonUpdate):
    with Session(engine) as session:
        pokemon = session.exec(select(Pokemon).where(Pokemon.id == pokemon_id)).one_or_none()
        if not pokemon:
            raise HTTPException(status_code=404, detail="Pokemon not found")

        update_data = updated.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(pokemon, key, value)

        session.add(pokemon)
        session.commit()
        session.refresh(pokemon)
        return pokemon


@app.post("/api/pokemon", status_code=201)
def create_pokemon(new_pokemon: PokemonCreate):
    total = (
        new_pokemon.hp
        + new_pokemon.attack
        + new_pokemon.defense
        + new_pokemon.sp_atk
        + new_pokemon.sp_def
        + new_pokemon.speed
    )

    pokemon = Pokemon(
        dex_number=new_pokemon.dex_number,
        name=new_pokemon.name.strip(),
        type1=new_pokemon.type1.strip() if new_pokemon.type1 else None,
        type2=new_pokemon.type2.strip() if new_pokemon.type2 else None,
        total=total,
        hp=new_pokemon.hp,
        attack=new_pokemon.attack,
        defense=new_pokemon.defense,
        sp_atk=new_pokemon.sp_atk,
        sp_def=new_pokemon.sp_def,
        speed=new_pokemon.speed,
        generation=new_pokemon.generation,
        legendary=new_pokemon.legendary,
    )

    with Session(engine) as session:
        session.add(pokemon)
        session.commit()
        session.refresh(pokemon)
        return pokemon


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("Main:app", host="0.0.0.0", port=8000, reload=True)
