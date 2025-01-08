import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch('http://localhost:5000/trends');
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch trends');
    }

    return NextResponse.json(data.data);
  } catch (error) {
    console.error('Error fetching trends:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch trends',
        details: error instanceof Error ? error.message : 'Unknown error'
      }, 
      { status: 500 }
    );
  }
} 