from bs4 import BeautifulSoup
import requests
import threading
import queue

class Crawler:
    def __init__(self, base_url, max_threads=5):
        self.base_url = base_url
        self.max_threads = max_threads
        self.q = queue.Queue()
        self.visited = set()
        self.q.put(base_url)
        self.visited.add(base_url)

        self.addURL = self.base_url
        if "https://" in self.addURL:
            self.addURL = self.addURL.split("https://")[1]
            self.addURL = self.addURL.split("/")[0]
            self.addURL = "https://" + self.addURL
        else:
            if "/" not in self.addURL:
                self.addURL = "https://" + self.addURL
            else:
                self.addURL = "https://" + self.addURL.split("/")[0]


        print(f"Using {max_threads} Threads")

    def initialise(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            if link.get('href'):
                link = self.addURL + link.get('href')
                self.q.put(link)

    def crawl(self):
        threads = [threading.Thread(target=self.worker) for _ in range(self.max_threads)]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

  
    def worker(self):
        while True:
            try:
                url = self.q.get_nowait()
                
            except queue.Empty:
                break

            if url not in self.visited:
                self.visited.add(url)
                try:
                  response = requests.get(url)
                  soup = BeautifulSoup(response.text, 'html.parser')
       
                  links = soup.find_all('a')
                  for link in links:
                      if link.get('href'):
              
                        if "/wiki/" in link.get("href"):
                          lnk = link.get("href")
                          title = lnk.split("/wiki/")[1]
                          if "%" not in title and ":" not in title:
                            with open("titles2.txt", "r+") as file:
                                lines = [i.rstrip("\n") for i in file.readlines()]
                                if title not in lines:
                                  file.write(str(title + "\n"))
                        
                        new_link = self.addURL + link.get('href')
                        
                        
                        if new_link not in self.visited and "wikipedia" not in link.get("href").lower() and "wikimedia" not in link.get("href").lower():
                            self.q.put(new_link)
                            print(new_link)
                      
              
                except Exception as e:
                  with open("errors.txt", "a") as f:
                    f.write(str(e))

            self.q.task_done()

    def __repr__(self):
        output = ""
        while not self.q.empty():
            output += self.q.get() + "\n"
        return output

crawler = Crawler("https://en.wikipedia.org/wiki/Orange_(fruit)", 10)
crawler.initialise()
crawler.crawl()
# print(crawler)
