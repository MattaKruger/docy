import { createPathBasedClient } from "openapi-fetch";
import type { paths } from "./schema";

const client = createPathBasedClient<paths>({
  baseUrl: "http://localhost:8000",
});

export default client;
