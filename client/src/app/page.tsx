'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { RefreshCcw, Loader2 } from 'lucide-react'
import { useTheme } from "next-themes"
import { MoonIcon, SunIcon } from "@radix-ui/react-icons"

interface Trend {
  category?: string
  headline?: string
  tweet_count?: string
  description?: string
}

interface TrendData {
  unique_id: string
  trends: Trend[]
  end_time: string
  timestamp: string
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [trends, setTrends] = useState<TrendData[]>([])
  const [error, setError] = useState<string | null>(null)
  const [scrapingStatus, setScrapingStatus] = useState<string>('')
  const { setTheme, theme } = useTheme()

  const fetchTrends = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/trends')
      if (!response.ok) {
        throw new Error('Failed to fetch trends')
      }
      const data = await response.json()
      setTrends(data)
    } catch (error) {
      setError('Failed to fetch trends')
      console.error('Fetch error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const startScraping = async () => {
    setIsLoading(true)
    setError(null)
    setScrapingStatus('Starting scraping process...')
    
    try {
      const response = await fetch('/api/scrape', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.details || data.error || 'Scraping failed')
      }

      setScrapingStatus('Scraping completed, fetching new data...')
      console.log('Scraping output:', data.output)
      
      await new Promise(resolve => setTimeout(resolve, 2000))
      await fetchTrends()
      
      setScrapingStatus('')
      
    } catch (error) {
      console.error('Scraping error:', error)
      setError(error instanceof Error ? error.message : 'Failed to start scraping')
      setScrapingStatus('')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchTrends()
  }, [])

  return (
    <div className="min-h-screen bg-background text-foreground py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Twitter Trends</h1>
          <div className="flex items-center gap-4">
            {scrapingStatus && (
              <p className="text-sm text-muted-foreground">{scrapingStatus}</p>
            )}
            <Button
              onClick={fetchTrends}
              disabled={isLoading}
              variant="outline"
              size="icon"
            >
              <RefreshCcw className="h-4 w-4" />
            </Button>
            <Button
              onClick={startScraping}
              disabled={isLoading}
            >
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {isLoading ? 'Scraping...' : 'Start New Scrape'}
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            >
              {theme === "light" ? (
                <MoonIcon className="h-[1.2rem] w-[1.2rem]" />
              ) : (
                <SunIcon className="h-[1.2rem] w-[1.2rem]" />
              )}
            </Button>
          </div>
        </div>

        {error && (
          <div className="bg-destructive/15 border border-destructive text-destructive px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="space-y-6">
          {isLoading && trends.length === 0 ? (
            Array.from({ length: 3 }).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-6 bg-muted rounded w-1/4"></div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Array.from({ length: 4 }).map((_, j) => (
                      <div key={j} className="space-y-2">
                        <div className="h-4 bg-muted rounded w-3/4"></div>
                        <div className="h-4 bg-muted rounded w-1/2"></div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            trends.map((trendData) => (
              <Card key={trendData.unique_id}>
                <CardHeader>
                  <CardTitle className="text-sm text-muted-foreground">
                    Scraped at: {new Date(trendData.timestamp).toLocaleString()}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {trendData.trends.map((trend, index) => (
                      <Card key={index}>
                        <CardContent className="p-4">
                          {trend.category && (
                            <p className="text-sm text-primary mb-1">{trend.category}</p>
                          )}
                          {trend.headline && (
                            <h3 className="font-semibold text-lg mb-2">{trend.headline}</h3>
                          )}
                          {trend.tweet_count && (
                            <p className="text-sm text-muted-foreground mb-2">{trend.tweet_count}</p>
                          )}
                          {trend.description && (
                            <p className="text-sm text-muted-foreground">{trend.description}</p>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

