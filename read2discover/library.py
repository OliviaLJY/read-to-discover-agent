from __future__ import annotations


ARTICLES = {
    "grounded-ai": {
        "section": "Ideas & Technology",
        "title": "The quiet craft of making AI trustworthy",
        "deck": "The most useful research assistants may be the ones that show their work - and make uncertainty feel like a feature, not a failure.",
        "author": "Maya Chen",
        "date": "November 14, 2026",
        "read_time": "7 min read",
        "accent": "#ef6f45",
        "paragraphs": [
            "Large language models are becoming useful research partners, but their confident errors make verification essential. A polished answer can still rest on a weak source, an outdated fact, or an assumption that was never made visible to the reader.",
            "Retrieval-augmented generation offers one practical response. Instead of asking a model to rely only on what it absorbed during training, a retrieval system first looks for relevant passages in a collection of documents. The model then builds its answer around that evidence. This does not eliminate mistakes, but it changes the shape of the problem: claims can be connected to sources that a reader can inspect.",
            "The difficult part is not retrieval alone. A system must decide what to search for, which passages deserve attention, and whether the retrieved evidence actually supports the final response. Evaluation datasets help teams measure factuality, citation accuracy, coverage, and uncertainty. Human review remains especially valuable when a task is ambiguous or high stakes.",
            "Interfaces matter just as much as models. A citation hidden behind a tiny icon technically provides provenance, yet does little to help a reader reason. Better designs place evidence close to the claim, expose disagreement between sources, and make it easy to move from a summary back to the original context.",
            "Trustworthy AI may therefore look less like a perfectly confident oracle and more like a careful collaborator. It retrieves, explains, and leaves a visible trail. The goal is not to remove uncertainty, but to help people navigate it deliberately.",
        ],
    },
    "urban-heat": {
        "section": "Cities & Climate",
        "title": "A cooler city begins on the block",
        "deck": "Heat maps are revealing how trees, roofs, pavement, and public policy shape radically different summers within the same city.",
        "author": "Elias Monroe",
        "date": "November 8, 2026",
        "read_time": "6 min read",
        "accent": "#3d8a68",
        "paragraphs": [
            "A heat wave does not arrive evenly. Two neighborhoods only a few miles apart can experience very different temperatures because concrete, asphalt, shade, building density, and traffic all influence how heat is absorbed and released.",
            "Researchers describe this pattern as the urban heat island effect. Satellite imagery gives a broad view, while street-level sensors reveal the temperature people actually encounter on sidewalks, bus stops, playgrounds, and apartment blocks. Together, these measurements make local inequalities visible.",
            "Tree canopy is one of the most effective forms of cooling, but planting is only the beginning. Young trees need years of care, reliable water, and enough soil to survive. Reflective roofs and lighter pavement can reduce absorbed heat more quickly, while shaded transit stops offer immediate protection during dangerous afternoons.",
            "The strongest plans combine physical design with public health. Cities can use neighborhood forecasts to open cooling centers, adjust outdoor work schedules, and direct outreach toward residents who live alone or lack air conditioning.",
            "Cooling a city is not a single engineering project. It is a long conversation between climate science, public space, housing, and neighborhood knowledge - one block at a time.",
        ],
    },
    "ocean-signals": {
        "section": "Science & Environment",
        "title": "Reading the ocean's smallest signals",
        "deck": "Microplastics are everywhere, but learning what they mean requires better sampling, sharper instruments, and more careful comparisons.",
        "author": "Noor Patel",
        "date": "October 29, 2026",
        "read_time": "8 min read",
        "accent": "#3977a8",
        "paragraphs": [
            "Microplastics have been found at the ocean surface, in deep sediments, and inside marine organisms. Their presence is clear; their movement and ecological effects are much harder to measure consistently.",
            "Different research teams collect particles with different nets, filters, and size thresholds. A method that misses the smallest fragments can produce a very different picture from one based on spectroscopy. Even the choice of polymer library changes which particles an instrument can identify.",
            "This makes standardization a scientific priority. Shared reference materials and transparent sampling protocols allow results from different coastlines and seasons to be compared. They also help researchers separate real environmental patterns from differences introduced by laboratory technique.",
            "Measurement is only one part of the story. Wastewater filtration can capture fibers before they reach rivers, while product design and source-reduction policy can prevent plastic from entering the system at all. Each intervention operates at a different scale and carries a different cost.",
            "The smallest particles are forcing researchers to think broadly: from analytical chemistry and food webs to infrastructure and regulation. The challenge is not merely to count what is present, but to understand which signals matter most.",
        ],
    },
}


def article_text(article: dict) -> str:
    return "\n\n".join([article["title"], article["deck"], *article["paragraphs"]])

