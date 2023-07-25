// from https://github.com/blu3mo/Scrapbox-Duplicator
import { importPages, assertString } from "./deps.ts";

const sid = Deno.env.get("SID");
const importingProjectName = "nishio";

assertString(sid);

// const jsonString = await Deno.readTextFile("data_en_diff.json");
// const data = JSON.parse(jsonString);

const data = {
  pages: [
    {
      title: "hello from bot",
      lines: ["hello from bot", "hello", "bye"],
    },
  ],
};

const importingPages = data.pages;

if (importingPages.length === 0) {
  console.log("No page to be imported found.");
} else {
  console.log(
    `Importing ${importingPages.length} pages to "/${importingProjectName}"...`
  );
  const result = await importPages(
    importingProjectName,
    {
      pages: importingPages,
    },
    {
      sid,
    }
  );
  if (!result.ok) {
    const error = new Error();
    error.name = `${result.value.name} when importing pages`;
    error.message = result.value.message;
    throw error;
  }
  console.log(result.value);
}
