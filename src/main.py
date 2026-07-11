from src.engine.gameloop import GameLoop


def main() -> None:
    gameloop = GameLoop(tick_rate=0.5)
    try:
        gameloop.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        gameloop.shutdown()


if __name__ == "__main__":
    main()
