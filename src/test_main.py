from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_gpu():
    response = client.get("/gpu")
    print("Read GPU:", response.json())


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_invalid_score_type():
    response = client.post(
        "/score/invalid-score-type",
        json={
            "textbook_name": "macroeconomics-2e",
            "chapter_index": "3",
            "section_index": "1",
            "summary": "Validity is important.",
        },
    )
    print("Invalid Score Type:", response.json())


def test_invalid_textbook_name():
    response = client.post(
        "/score/summary",
        json={
            "textbook_name": "invalid-textbook-name",
            "chapter_index": "4",
            "section_index": "2",
            "summary": "Validity is important.",
        },
    )
    print("Invalid Textbook Name:", response.json())


def test_irrelevant_summary():
    response = client.post(
        "/score/summary",
        json={
            "textbook_name": "macroeconomics-2e",
            "chapter_index": "5",
            "section_index": "2",
            "summary": """The z-index property in CSS controls the vertical stacking order of elements that overlap. As in, which one appears as if it is physically closer to you. z-index only affects elements that have a position value other than static (the default).Elements can overlap for a variety of reasons, for instance, relative positioning has nudged it over something else. Negative margin has pulled the element over another. Absolutely positioned elements overlap each other. All sorts of reasons.""",  # noqa: E501
        },
    )
    print("Irrelevant Summary:", response.json())


def test_containment():
    response = client.post(
        "/score/summary",
        json={
            "textbook_name": "macroeconomics-2e",
            "chapter_index": "1",
            "section_index": "1",
            "summary": """Think about it this way: In 2015 the labor force in the United States contained over 158 million workers, according to the U.S. Bureau of Labor Statistics. The total land area was 3,794,101 square miles. While these are certainly large numbers, they are not infinite. Because these resources are limited, so are the numbers of goods and services we produce with them. Combine this with the fact that human wants seem to be virtually infinite, and you can see why scarcity is a problem.',""",  # noqa: E501
        },
    )
    print("Copied Text:", response.json())
    assert response.json()["containment"] > 0.9


def test_focus_time():
    response = client.post(
        "/score/summary",
        json={
            "textbook_name": "macroeconomics-2e",
            "chapter_index": "1",
            "section_index": "1",
            "summary": """Sexy is considered a bad word in this context.""",
            "focus_time": {
                "overview": 1,
                "introduction-to-fred": 48,
                "the-problem-of-scarcity": 29,
                "learn-with-videos": 1,
                "the-division-of-and-specialization-of-labor": 40,
                "why-the-division-of-labor-increases-production": 1,
                "trade-and-markets": 19,
                "learn-with-videos-1": 254,
                "why-study-economics": 15,
                "learn-with-videos-2": 516,
            },
        },
    )
    print("Profane Text:", response.json())


def test_long_summary():
    response = client.post(
        "/score/summary",
        json={
            "textbook_name": "macroeconomics-2e",
            "chapter_index": "1",
            "section_index": "1",
            "summary": """in this section, you will learn the following:\n\n- discuss the importance of studying economics\n\n- explain the relationship between production and division of labor\n\n- evaluate the significance of scarcity\n\neconomics is defined by wikipidia as "a social science that studies the production, distribution, and consumption of goods and services.". these can be why a company decides to sell a product at a certain price point (distribution), how many of the product it makes (production), and how many consumers will buy the product (consumption). scarcity means that the demand has exceeded the supply. resources, such as time, labor, materials, etc, exist in a finite supply and may run out. \n\nin 2015 the labor force in the united states contained over 158 million workers, according to the u.s. bureau of labor statistics, but the population of the u.s. in 2015 was about 320 million. now some of these are children and adults unable to work, but those people still want for things. so the labor force needs to meet the demand of a population more than twice its size. this is why there\'s a scarcity problem. \n\none very important thing in economics is data. data allows us to describe and measure issues faced so that we can further understand them. many government agencies publish economic and social data. during this course, we will be using the st. louis federal reserve bank\'s fred database. fred has a database that is very simple to use. you can display data in tables, charts, and print of spreadsheets. can easily download it into spreadsheet form if you want to use the data for other purposes. the fred website includes data on nearly 400,000 domestic and international variables over time, in the following broad categories:\n\n- money, banking & finance\n\n- population, employment, & labor markets (including income distribution)\n\n- national accounts (gross domestic product & its components), flow of funds, and ---- -----_ - international accounts production & business activity (including business cycles)\n\n- prices & inflation (including the consumer price index, the producer price index, and the - employment cost index)\n\n- international data from other nations\n\n- u.s. regional data academic data (including penn world tables & nber macrohistory database)\n\nfor more information on fred, you can view the youyube vidoes for this course.\n\nif you still don\'t think that scarcity is a problem, think about whether or not everyone has enough food to eat, warm clothing during the winter, etc.\n\nexample: mark runs a bakery. his most popular item is the spinach quiche. there is a salmonella outbreak in the local spinach supply, so the local stores are no longer selling spinach, thus the materials he needs to make his spinach quiche have run out for now, so he can not meet the demand of his customers. this is just one example of scarcity.\n\nbelow we\'ll continue to discuss the scarcity problem.\n\nhow do you buy things that you want? you work a job or them and are paid money that you can then spend on things you want. you don\'t make these things yourself, you buy them from somewhere that pays others to do so for you. a lot of us don\'t have the income to buy all of the things that we want though. this is because of scarcity. how can we solve this?\n\nevery society, at every level, must make decisions on how to spend their resources. do you save up for that new car, or do you go on vacation with your friends and family? towns and cities must decide how much of their annual budget goes to law enforcement, fire and safety, infrastructure, etc. even nations must decide how much money that the spend on defense, environmental issues, and their people. in most cases, the budget is just not enough to give equally to everything. \n\nso how can we produce enough for everyone? well, we can each produce the things that we need ourselves or we could produce some of what we need, and trade for the rest with others. why don\'t we do this? think back to our pioneering days, people back then were much more self efficient than we are now. they could build, farm, sew, hunt, etc. most people nowadays barely even know how their own car works. so we need specialized laborers to do certain jobs so that others are free to do other jobs. it\'s not that we can\'t learn how to fix our own cars and hunt for ourselves, but it\'s because we don\'t have to that we don\'t. the reason for this is the division and specialization of labor, a production innovation first put forth by adam smith in his book, "the wealth of nations".\n\nwe\'ll discuss the division of and specialization of labor now. \n\neconomics as a formal branch of study first began when adam smith  (1723-1790) published his book "the wealth of nations" back in 1176. it\'d been written about before of course, but he was the first to approach if in a comprehensive way. in the first chapter, he introduced the concept of division of labor, which means the way something is made is divided into who makes it, who provides the materials, and who pays the workers to make the product, instead of one person doing all of the work.\n\nto explain the division of labor, imagine again a bakery. you need someone to make the flour for the baked goods, but you also need a farmer to farm the wheat to make the flour. you need a store to stock the flour, and then the baker needs to go purchase the flour. that\'s already several people that are involved in the making of the baked good, and we\'ve only thought of the flour! what about all of the other ingredients?\n\nlots of businesses divide their labor. restaurants have hosts to seat the customers, waiters to take their orders, cooks to prepare the food, managers to oversee everyone, and busboys/busgirls to clear the plates when the customer is done. hospitals have doctors, nurses, technicians, etc.\n\nwhy does the division of labor increase production?\n\nwhen labor is divided more things can be done. think of a factory that makes and bottles your favorite soda. you\'d have the people certified to make the soda by mixing the ingredients, you\'d have the testers, the ones who run the machine to put the liquid in the bottles, and the ones who do quality checks to make sure that the bottles are properly sealed. if the factory only had one person in each of these tasks, they wouldn\'t be able to make much, but if they divide the labor, they can increase the amount of people who work in each station and thus make more product.\n\nsmith offered three reasons.\n\nthe first is because workers who have specialized certifications or knowledge in certain areas are better able to focus and work in those areas. such as, a neurologist is better able to focus on helping patients who have neurological issues whereas a gastroenterology is better able to help patients with gastrointestinal issues. even though both are doctors, they specialize in different areas. \n\nthe second is workers who specialize in one area are able to get things done quicker and more efficiently. and specialization in a certain job allows workers to focus on their particular job and not have to worry about other aspects. the one in charge of putting caps on the bottles doesn\'t need to worry about putting labels on the bottles, testing the soda to make sure it tastes right, etc. similarly a company that focuses on one type of product is able to produce more efficiently than a company that focuses on more than one. this is often referred to as "core competency".\n\nand finally, the third reason put forth by smith is that specialization allows companies to take advantage of the market demand, if a product is much needed, and a company finds a more efficient way to make it, they can begin to see more profit for it. for example. if a company makes designer shoes and can only produce 50 shoes a month, the cost of the shoes will be very high, and they\'ll only be able to sell 50 shoes a month. but, if they\'re able to make 150 shoes a month, for the same cost, they can then sell at a lower price and sell more shoes each month, thus seeing a bigger profit. this is why the division of labor has been a great force against scarcity. more products are able to be made when the labor is divided.\n\ntrade and markets\n\nspecialization only makes sense if the workers can then use their income to buy things that they aren\'t able to make but someone else can. meaning, specialization requires trade in order to work.\n\nyou don\'t have to know how your tv works, you just need to know how to turn it on and work the remote after you\'ve bought it. you don\'t need to know how to sew in order to have clothing, you just have to have the money to buy it from the store. \n\ninstead of you needing to learn all of the skills to make the things that you want and need, division of labor and specialization allow you to learn a specialized set of skills, find a job using those skills, and then use that money you earn to buy the things that you need or want. this is how modern society has become a strong economy.\n\nso, why should you study economics?\n\nyou\'ve been given a brief overview of economics, so what\'s a good reason to study it further? well first off, economics isn\'t just a bunch of facts that you need to memorize, although there are some, it\'s a way to understand the world around you. it\'s a collection of puzzles and the answers needed to solve those puzzles. \n\nif you\'re still on the fence, here are a few other reasons to study economics:\n\n- economics is crucial for understanding the things going on in the world today. war, poverty, global warming, all of these have economics at their core. and understanding economics will help you to understand these things more clearly too.\n\n- being a citizen in today\'s world, understanding economics and how the world economy effects you is important. when the u.s. government came to a standstill at the end of 2012, did you understand why? did you understand how it effected you?\n\n- a basic understanding of economics and other subjects can help to make you a well-rounded thinker. when you read or hear about economic issues in the world, you\'ll be better able to understand what is going on, and how it effects you. you\'ll be able to distinguish between nonsense and sense when talking about it with your friends, family, and co-workers.\n\nthe study of economics won\'t tell you the answers, but it can help you to come to your own understanding of them.""",  # noqa: E501
        },
    )
    print("Really Long Summary:", response.json())


def test_short_answer():
    response = client.post(
        "/score/answer",
        json={
            "textbook_name": "macroeconomics-2e",
            "chapter_index": 1,
            "section_index": 1,
            "subsection_index": 1,
            "answer": "happy",
        },
    )
    print("Short answer test results:", response.json())


def test_main():
    test_read_main()
    test_read_gpu()
    test_invalid_score_type()
    test_invalid_textbook_name()


def test_summary_score():
    test_irrelevant_summary()
    test_focus_time()
    test_containment()
    test_long_summary()


def test_answer_score():
    test_short_answer()


if __name__ == "__main__":
    test_main()
    test_summary_score()
    test_answer_score()
