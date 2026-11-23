export async function call<T>(
  op: string,
  token: string,
  data: unknown = {},
): Promise<T> {
  if (location.origin !== "http://127.0.0.1:8787")
    throw new Error(
      "Open the local console at http://127.0.0.1:8787 to pair this workspace.",
    );
  let response: Response;
  try {
    response = await fetch("http://127.0.0.1:8766/knowledge/" + op, {
      method: "POST",
      cache: "no-store",
      credentials: "omit",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: "Bearer " + token } : {}),
      },
      body: JSON.stringify(data),
    });
  } catch {
    throw new Error(
      "Local repository unavailable. Start the knowledge service and reconnect.",
    );
  }
  const body = (await response.json()) as T & { error?: string };
  if (!response.ok) throw new Error(body.error || "Local operation failed.");
  return body;
}
