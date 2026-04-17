import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App routes", () => {
  it("renders mode studio at /studio", async () => {
    render(
      <MemoryRouter initialEntries={["/studio"]}>
        <App />
      </MemoryRouter>
    );
    expect(await screen.findByRole("heading", { level: 1, name: /saddle studio/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /load template/i })).toBeInTheDocument();
  });
});
